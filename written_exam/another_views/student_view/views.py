from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError
from django.db import transaction
from django.db.models import Count
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Sum
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsStudent
from written_exam.another_views.student_view.serializers import AttemptQuestionSerializer
from written_exam.another_views.student_view.serializers import FinishExamSerializer
from written_exam.another_views.student_view.serializers import GetAnswerSerializer
from written_exam.another_views.student_view.serializers import StudentExamResultSerializer
from written_exam.another_views.student_view.serializers import StudentWrittenExamSerializerList
from written_exam.models import AttemptQuestion
from written_exam.models import ExamSession
from written_exam.models import WrittenExam
from written_exam.models import WrittenExamAccess
from written_exam.models import WrittenExamAnswer
from written_exam.models import WrittenExamAttempt
from written_exam.models import WrittenExamGroup
from written_exam.utils import generate_exam_questions
from written_exam.utils import get_client_ip


class StudentExamNameAPIView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Imtihon nomini olish (ID bo‘yicha)",
        manual_parameters=[
            openapi.Parameter(
                "exam_id",
                openapi.IN_PATH,
                description="Imtihon ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Imtihon nomi",
                examples={"application/json": {"name": "Imtihon nomi"}}
            ),
            404: "Imtihon topilmadi",
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id):
        name = (
            WrittenExam.objects
            .filter(pk=exam_id)
            .values_list("name", flat=True)
            .first()
        )

        if name is None:
            return Response(
                {"error": "Imtihon topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({"name": name}, status=status.HTTP_200_OK)


class StudentExamList(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Talaba uchun yozma imtihonlar",
        responses={200: StudentWrittenExamSerializerList(many=True)},
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request):
        student = getattr(request.user, "student", None)

        if not student:
            return Response(
                {"error": "Student topilmadi"},
                status=status.HTTP_403_FORBIDDEN
            )

        now = timezone.now()

        blocked_subquery = WrittenExamAccess.objects.filter(
            exam=OuterRef("pk"),
            student=student,
            is_accessible=False
        )

        exams = (
            WrittenExam.objects
            .filter(
                assigned_exams__group_id=student.group_id,
                status=True,
                begin_time__lte=now,
                end_time__gte=now
            )
            .annotate(
                is_blocked=Exists(blocked_subquery),
                attempt_count=Count(
                    "attempts",
                    filter=Q(attempts__student=student),
                    distinct=True
                )
            )
            .prefetch_related(
                Prefetch(
                    "attempts",
                    queryset=WrittenExamAttempt.objects.filter(
                        student=student
                    ).select_related("session").order_by("-attempt_no"),
                    to_attr="student_attempts"
                )
            )
            .distinct()
            .order_by("-begin_time")
        )

        serializer = StudentWrittenExamSerializerList(
            exams,
            many=True,
            context={"student": student}
        )

        return Response(serializer.data)


class StudentStartExamView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Imtihonni boshlash yoki davom ettirish",
        manual_parameters=[
            openapi.Parameter(
                "Device-Fingerprint",
                openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request, exam_id):

        student = getattr(request.user, "student", None)
        if not student:
            return Response({"error": "Student topilmadi"}, status=403)

        try:
            exam = WrittenExam.objects.get(pk=exam_id, status=True)
        except WrittenExam.DoesNotExist:
            return Response({"error": "Imtihon topilmadi"}, status=404)

        now = timezone.now()

        if not (exam.begin_time <= now <= exam.end_time):
            return Response({"error": "Imtihon vaqti mos emas"}, status=400)

        if not WrittenExamGroup.objects.filter(
            exam=exam,
            group_id=student.group_id
        ).exists():
            return Response({"error": "Imtihon sizga tegishli emas"}, status=403)

        if WrittenExamAccess.objects.filter(
            exam=exam,
            student=student,
            is_accessible=False
        ).exists():
            return Response({"error": "Imtihonga ruxsat yo‘q"}, status=403)

        fingerprint = request.headers.get("Device-Fingerprint")
        if not fingerprint:
            return Response({"error": "Qurilma aniqlanmadi"}, status=403)

        ip = get_client_ip(request)

        with transaction.atomic():

            attempts = (
                WrittenExamAttempt.objects
                .select_for_update()
                .filter(exam=exam, student=student)
                .order_by("-attempt_no")
            )

            attempts = list(attempts)
            attempt_count = len(attempts)

            active = next(
                (a for a in attempts if a.status == "in_progress"),
                None
            )

            # =========================
            # ACTIVE ATTEMPT (RESUME)
            # =========================

            if active:

                if now > active.expires_at:
                    active.status = "expired"
                    active.save(update_fields=["status"])
                    active = None

                else:
                    try:
                        session = (
                            ExamSession.objects
                            .select_for_update()
                            .get(attempt=active)
                        )
                    except ExamSession.DoesNotExist:
                        return Response({"error": "Session buzilgan"}, status=403)

                    if session.locked:
                        return Response({"error": "Session bloklangan"}, status=403)

                    # 🔥 DEVICE CHECK (UPDATED)
                    if session.device_hash != fingerprint:

                        # ✅ ADMIN RESET
                        if getattr(session, "allow_device_reset", False):
                            session.device_hash = fingerprint
                            session.allow_device_reset = False
                            session.locked = False
                            session.last_activity = now
                            session.save(update_fields=[
                                "device_hash",
                                "allow_device_reset",
                                "locked",
                                "last_activity"
                            ])

                            active.device_fingerprint = fingerprint
                            active.ip_address = ip
                            active.save(update_fields=["device_fingerprint", "ip_address"])

                        # ✅ SAME IP (lab case)
                        elif active.ip_address == ip:
                            session.device_hash = fingerprint
                            session.last_activity = now
                            session.save(update_fields=["device_hash", "last_activity"])

                            active.device_fingerprint = fingerprint
                            active.save(update_fields=["device_fingerprint"])

                        # ❌ DIFFERENT IP
                        else:
                            active.status = "terminated"
                            active.save(update_fields=["status"])

                            session.locked = True
                            session.save(update_fields=["locked"])

                            return Response(
                                {"error": "Boshqa qurilmadan kirish aniqlandi"},
                                status=403
                            )

                    # 🔥 INACTIVITY CHECK
                    last_activity = session.last_activity or session.created_at
                    if (now - last_activity).total_seconds() > exam.inactivity_timeout_minutes * 60:
                        active.status = "terminated"
                        active.save(update_fields=["status"])

                        session.locked = True
                        session.save(update_fields=["locked"])

                        return Response({"error": "Faollik vaqti tugadi"}, status=403)

                    # 🔄 update activity + IP
                    session.last_activity = now
                    session.save(update_fields=["last_activity"])

                    active.ip_address = ip
                    active.save(update_fields=["ip_address"])

                    questions = (
                        AttemptQuestion.objects
                        .filter(attempt=active)
                        .order_by("order")
                    )

                    serializer = AttemptQuestionSerializer(questions, many=True)

                    remaining_seconds = int(
                        (active.expires_at - now).total_seconds()
                    )

                    return Response({
                        "attempt_id": active.id,
                        "attempt_no": active.attempt_no,
                        "remaining_seconds": remaining_seconds,
                        "questions": serializer.data
                    })

            # =========================
            # NEW ATTEMPT
            # =========================

            if attempt_count >= exam.max_attempts:
                return Response({"error": "Urinishlar tugagan"}, status=400)

            questions = generate_exam_questions(exam)

            if len(questions) != exam.total_questions:
                return Response({"error": "Savollar yetarli emas"}, status=400)

            try:
                new_attempt = WrittenExamAttempt.objects.create(
                    exam=exam,
                    student=student,
                    attempt_no=attempt_count + 1,
                    expires_at=min(
                        now + timedelta(minutes=exam.duration_minutes),
                        exam.end_time
                    ),
                    device_fingerprint=fingerprint,
                    ip_address=ip,
                    status="in_progress"
                )
            except IntegrityError:
                return Response({"error": "Attempt yaratishda xatolik"}, status=400)

            ExamSession.objects.create(
                attempt=new_attempt,
                device_hash=fingerprint,
                last_activity=now,
                locked=False
            )

            AttemptQuestion.objects.bulk_create([
                AttemptQuestion(
                    attempt=new_attempt,
                    question=q,
                    order=i
                )
                for i, q in enumerate(questions, 1)
            ])

            WrittenExamAnswer.objects.bulk_create([
                WrittenExamAnswer(
                    attempt=new_attempt,
                    question=q,
                    answer_text=""
                )
                for q in questions
            ])

            questions_qs = (
                AttemptQuestion.objects
                .filter(attempt=new_attempt)
                .order_by("order")
            )

            serializer = AttemptQuestionSerializer(questions_qs, many=True)

            return Response({
                "attempt_id": new_attempt.id,
                "attempt_no": new_attempt.attempt_no,
                "remaining_seconds": int((new_attempt.expires_at - now).total_seconds()),
                "questions": serializer.data
            }, status=201)


class ExamQuestionsAPIView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Talaba uchun yozma imtihonni savolari va javoblari",
        operation_description="Talabaga tegishli yozma imtihon savolari va javoblari",
        responses={
            200: AttemptQuestionSerializer(many=True),
            403: "Ruxsat yo‘q"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id, *args, **kwargs):
        student = getattr(request.user, "student", None)
        if not student:
            return Response(
                {"error": "Student topilmadi"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            exam = WrittenExam.objects.get(id=exam_id)
        except Exception as ex:
            return Response({"error": "Imthon topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
        if exam.status == False:
            return Response("Imthon foal emas!", status=status.HTTP_400_BAD_REQUEST)

        acces_check = WrittenExamAccess.objects.filter(exam=exam, student=student, is_accessible=True).exists()
        if not acces_check:
            return Response({"error": "Ruxsat yo‘q"}, status=403)

        attempts_qs = WrittenExamAttempt.objects.filter(
            exam=exam,
            student=student
        )

        # oxirgi in_progress attempt
        attempt_last = attempts_qs.filter(
            status='in_progress'
        ).order_by('-created_at').first()
        now = timezone.now()
        if attempt_last:
            if now > attempt_last.expires_at:
                return Response(
                    {"error": "Imtihon uchun berilgan urinish vaqti tugagan!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            attempt_questions = AttemptQuestion.objects.filter(
                attempt=attempt_last
            ).order_by('order')

            serializer = AttemptQuestionSerializer(attempt_questions, many=True)
            return Response({"data": serializer.data}, status=200)

        else:
            return Response(
                {"error": "Imtihon uchun berilgan urinish tugagan!"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ExamOneQuestionAPIView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Talaba uchun yozma imtihonni bita savoli javobi bilan",
        operation_description="Talabaga tegishli yozma imtihon bita savoli javobi bilan",
        responses={
            200: AttemptQuestionSerializer(many=False),
            403: "Ruxsat yo‘q"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, question_id, *args, **kwargs):
        student = getattr(request.user, "student", None)
        if not student:
            return Response(
                {"error": "Student topilmadi"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            question = AttemptQuestion.objects.get(id=question_id)
        except Exception as ex:
            return Response({"error": "Savol topilmadi!"}, status=status.HTTP_404_NOT_FOUND)

        if question.attempt.exam.status == False:
            return Response("Imthon foal emas!", status=status.HTTP_400_BAD_REQUEST)

        acces_check = WrittenExamAccess.objects.filter(exam=question.attempt.exam, student=student,
                                                       is_accessible=True).exists()
        if not acces_check:
            return Response({"error": "Ruxsat yo‘q"}, status=403)

        attempts_qs = WrittenExamAttempt.objects.filter(
            exam=question.attempt.exam,
            student=student
        )

        # oxirgi in_progress attempt
        attempt_last = attempts_qs.filter(
            status='in_progress'
        ).order_by('-created_at').first()
        now = timezone.now()
        if attempt_last:
            if now > attempt_last.expires_at:
                return Response(
                    {"error": "Imtihon uchun berilgan urinish vaqti tugagan!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = AttemptQuestionSerializer(question, many=False)
            return Response({"data": serializer.data}, status=200)

        else:
            return Response(
                {"error": "Imtihon uchun berilgan urinish tugagan!"},
                status=status.HTTP_400_BAD_REQUEST
            )


class SaveAnswerAPIView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Savol javobini saqlash",
        operation_description="""
Talaba yozma imtihon savoliga javob yozadi.

Xususiyatlar:
• faqat aktiv attemptga yozish mumkin
• device fingerprint tekshiriladi
• vaqt tugasa oxirgi javob qabul qilinadi
• vaqt tugaganda attempt avtomatik submitted bo‘ladi
        """,
        manual_parameters=[
            openapi.Parameter(
                "Device-Fingerprint",
                openapi.IN_HEADER,
                description="Qurilma fingerprinti",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=GetAnswerSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                    "exam_state": openapi.Schema(type=openapi.TYPE_STRING),
                    "reason": openapi.Schema(type=openapi.TYPE_STRING),
                    "remaining_seconds": openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            403: "Ruxsat yo‘q",
            404: "Savol topilmadi"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def patch(self, request):

        student = getattr(request.user, "student", None)

        if not student:
            return Response({"error": "Student topilmadi"}, status=403)

        fingerprint = request.headers.get("Device-Fingerprint")

        if not fingerprint:
            return Response({"error": "Qurilma aniqlanmadi"}, status=403)

        serializer = GetAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_id = serializer.validated_data["question_id"]
        answer_text = serializer.validated_data["answer"]

        now = timezone.now()

        with transaction.atomic():

            attempt = (
                WrittenExamAttempt.objects
                .select_for_update()
                .filter(
                    student=student,
                    status="in_progress"
                )
                .order_by("-created_at")
                .first()
            )

            if not attempt:
                return Response(
                    {"error": "Aktiv imtihon topilmadi"},
                    status=400
                )

            try:
                session = (
                    ExamSession.objects
                    .select_for_update()
                    .get(attempt=attempt)
                )
            except ExamSession.DoesNotExist:
                return Response(
                    {"error": "Session topilmadi"},
                    status=403
                )

            if session.locked:
                return Response(
                    {"error": "Session bloklangan"},
                    status=403
                )

            # DEVICE CHECK
            if session.device_hash != fingerprint:
                attempt.status = "terminated"
                attempt.save(update_fields=["status"])

                session.locked = True
                session.save(update_fields=["locked"])

                return Response({
                    "status": "terminated",
                    "exam_state": "finished",
                    "reason": "device_changed"
                })

            try:
                attempt_question = (
                    AttemptQuestion.objects
                    .select_related("question")
                    .get(
                        id=question_id,
                        attempt=attempt
                    )
                )
            except AttemptQuestion.DoesNotExist:
                return Response(
                    {"error": "Savol topilmadi"},
                    status=404
                )

            answer_obj = WrittenExamAnswer.objects.get(
                attempt=attempt,
                question=attempt_question.question
            )

            answer_obj.answer_text = answer_text
            answer_obj.save(update_fields=["answer_text"])

            # activity update
            session.last_activity = now
            session.save(update_fields=["last_activity"])

            remaining_seconds = max(
                int((attempt.expires_at - now).total_seconds()),
                0
            )

            if remaining_seconds <= 0:
                attempt.status = "submitted"
                attempt.submitted_at = now
                attempt.save(update_fields=["status", "submitted_at"])

                return Response({
                    "status": "submitted",
                    "exam_state": "finished",
                    "reason": "time_expired",
                    "remaining_seconds": 0
                })

            return Response({
                "status": "saved",
                "exam_state": "in_progress",
                "remaining_seconds": remaining_seconds
            })


class ExamTimeAPIView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Talaba uchun yozma imtihonni bita savoli javobi bilan",
        operation_description="Talabaga tegishli yozma imtihon bita savoli javobi bilan",
        responses={
            200: AttemptQuestionSerializer(many=False),
            403: "Ruxsat yo‘q"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id, *args, **kwargs):
        student = getattr(request.user, "student", None)
        if not student:
            return Response(
                {"error": "Student topilmadi"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            exam = WrittenExam.objects.get(id=exam_id)
        except Exception as ex:
            return Response({"error": "Imthon topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
        if not exam.status:
            return Response("Imthon foal emas!", status=status.HTTP_400_BAD_REQUEST)

        access_check = WrittenExamAccess.objects.filter(exam=exam, student=student, is_accessible=True).exists()
        if not access_check:
            return Response({"error": "Ruxsat yo‘q"}, status=403)

        attempts_qs = WrittenExamAttempt.objects.filter(
            exam=exam,
            student=student
        )

        # oxirgi in_progress attempt
        attempt_last = attempts_qs.filter(
            status='in_progress'
        ).order_by('-created_at').first()

        return Response({"data": {"expires_time": attempt_last.expires_at}}, status=status.HTTP_200_OK)


class FinishExamAPIView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Yozma imtihonni tugatish",
        operation_description="""
Talaba yozma imtihonni yakunlaydi.

Xususiyatlar:
• faqat aktiv attemptni tugatish mumkin  
• device fingerprint tekshiriladi  
• boshqa qurilmadan kirish aniqlansa attempt terminate bo‘ladi
        """,
        manual_parameters=[
            openapi.Parameter(
                "Device-Fingerprint",
                openapi.IN_HEADER,
                description="Qurilma fingerprinti",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=FinishExamSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                    "exam_state": openapi.Schema(type=openapi.TYPE_STRING),
                    "reason": openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            403: "Ruxsat yo‘q",
            404: "Imtihon topilmadi"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request):

        student = getattr(request.user, "student", None)

        if not student:
            return Response({"error": "Student topilmadi"}, status=403)

        fingerprint = request.headers.get("Device-Fingerprint")

        if not fingerprint:
            return Response({"error": "Qurilma aniqlanmadi"}, status=403)

        serializer = FinishExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exam_id = serializer.validated_data["exam_id"]

        try:
            exam = WrittenExam.objects.get(id=exam_id, status=True)
        except WrittenExam.DoesNotExist:
            return Response({"error": "Imtihon topilmadi"}, status=404)

        access = WrittenExamAccess.objects.filter(
            exam=exam,
            student=student,
            is_accessible=True
        ).exists()

        if not access:
            return Response({"error": "Ruxsat yo‘q"}, status=403)

        now = timezone.now()

        with transaction.atomic():

            attempt = (
                WrittenExamAttempt.objects
                .select_for_update()
                .filter(
                    exam=exam,
                    student=student,
                    status="in_progress"
                )
                .order_by("-created_at")
                .first()
            )

            if not attempt:
                return Response(
                    {"error": "Aktiv attempt topilmadi"},
                    status=400
                )

            try:
                session = (
                    ExamSession.objects
                    .select_for_update()
                    .get(attempt=attempt)
                )
            except ExamSession.DoesNotExist:
                return Response(
                    {"error": "Session topilmadi"},
                    status=403
                )

            if session.locked:
                return Response(
                    {"error": "Session bloklangan"},
                    status=403
                )

            # DEVICE CHECK
            if session.device_hash != fingerprint:
                attempt.status = "terminated"
                attempt.save(update_fields=["status"])

                session.locked = True
                session.save(update_fields=["locked"])

                return Response({
                    "status": "terminated",
                    "exam_state": "finished",
                    "reason": "device_changed"
                })

            attempt.status = "submitted"
            attempt.submitted_at = now
            attempt.save(update_fields=["status", "submitted_at"])

            return Response({
                "status": "submitted",
                "exam_state": "finished"
            })


class ExamActivityView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Imtihon faoliyatini yangilash (heartbeat)",
        operation_description="""
Talaba imtihon ishlayotganini backendga bildiradi.
Frontend har 30 sekundda ushbu API ni chaqiradi.

Bu endpoint:
- session last_activity ni yangilaydi
- inactivity timeout ishlashi uchun kerak
        """,
        manual_parameters=[
            openapi.Parameter(
                "Device-Fingerprint",
                openapi.IN_HEADER,
                description="Qurilma fingerprinti",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            403: "Ruxsat yo‘q"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request):

        student = getattr(request.user, "student", None)

        if not student:
            return Response({"error": "Student topilmadi"}, status=403)

        fingerprint = request.headers.get("Device-Fingerprint")

        if not fingerprint:
            return Response({"error": "Qurilma aniqlanmadi"}, status=403)

        session = (
            ExamSession.objects
            .select_related("attempt")
            .filter(
                attempt__student=student,
                attempt__status="in_progress",
                device_hash=fingerprint,
                status=True,
                locked=False
            )
            .order_by("-created_at")
            .first()
        )

        if not session:
            return Response({"status": "Faol sessiya topilmadi"}, status=403)

        session.last_activity = timezone.now()
        session.save(update_fields=["last_activity"])

        return Response({"status": "ok"})


class StudentExamResultListAPIView(APIView):
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Talabaning barcha imtihon natijalari",
        responses={200: StudentExamResultSerializer(many=True)},
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request):

        student = getattr(request.user, "student", None)

        if not student:
            return Response(
                {"error": "Student topilmadi"},
                status=403
            )

        attempts = (
            WrittenExamAttempt.objects
            .filter(
                student=student,
                status__in=["submitted", "expired", "terminated"]
            )
            .select_related("exam")
            .annotate(
                total_questions=Count("answers", distinct=True),
                graded_answers=Count(
                    "answers",
                    filter=Q(answers__score__isnull=False),
                    distinct=True
                ),
                calculated_score=Sum("answers__score")
            )
            .order_by("-started_at")
        )

        results = []

        for attempt in attempts:
            total_questions = attempt.total_questions or 0
            graded_answers = attempt.graded_answers or 0
            total_score = attempt.calculated_score or Decimal("0.00")

            results.append({
                "id": attempt.exam_id,
                "name": attempt.exam.name,
                "attempt_no": attempt.attempt_no,
                "status": attempt.status,
                "total_questions": total_questions,
                "graded_answers": graded_answers,
                "ungraded_answers": total_questions - graded_answers,
                "total_score": total_score,
                "submitted_at": attempt.submitted_at
            })

        return Response(results)
