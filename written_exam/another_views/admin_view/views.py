from django.db import transaction
from django.db.models import Sum, Count, Q, OuterRef, Subquery, Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from shared.utils import CustomPageNumberPagination
from students.models import Student
from user.permission import IsAdmin
from written_exam.filters import WrittenExamFilter
from written_exam.models import ExamSession, WrittenExamQuestion
from written_exam.models import WrittenExam
from written_exam.another_views.admin_view.serializers import BaseWrittenExamUpdateSerializer, \
    WrittenExamQuestionSerializer
from written_exam.another_views.admin_view.serializers import WrittenExamCreateSerializer
from written_exam.another_views.admin_view.serializers import WrittenExamDetailSerializer
from written_exam.another_views.admin_view.serializers import WrittenExamListSerializer
from written_exam.another_views.admin_view.serializers import WrittenExamStatusUpdateSerializer
from written_exam.models import WrittenExamAccess
from written_exam.models import WrittenExamAnswer
from written_exam.models import WrittenExamAttempt
from written_exam.models import WrittenExamGroup
from written_exam.utils import CustomQPageNumberPagination
from rest_framework.exceptions import ValidationError, NotFound


class WrittenExamCreateAPIView(APIView):
    """
    Yangi yozma imtihon yaratish
    """
    permission_classes = [IsAdmin, ]

    @swagger_auto_schema(
        operation_summary="Yozma imtihon yaratish",
        operation_description="""
Admin tomonidan yangi yozma imtihon yaratiladi.

⚠️ Eslatma:
- Kamida bitta guruh biriktirilishi kerak
- Savollar soni 0 bo‘lmasligi kerak
- Duration imtihon vaqt oralig‘iga mos bo‘lishi kerak
        """,
        request_body=WrittenExamCreateSerializer,
        responses={
            201: openapi.Response(
                description="Imtihon muvaffaqiyatli yaratildi",
                examples={
                    "application/json": {
                        "message": "Imtihon muvaffaqiyatli yaratildi"
                    }
                }
            ),
            400: "Noto‘g‘ri ma'lumot yuborildi",
            403: "Ruxsat yo‘q"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request):
        serializer = WrittenExamCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Imtihon muvaffaqiyatli yaratildi"},
            status=status.HTTP_201_CREATED
        )


class WrittenExamStatusUpdateAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Imtihon statusini o‘zgartirish",
        operation_description="""
Imtihon statusi alohida endpoint orqali yangilanadi.

✅ Status=True (yoqish): savollar soni tekshiriladi.
✅ Status=False (o'chirish): admin har qachon o'chira oladi (emergency uchun).
   Bu paytda barcha aktiv sessiyalar yumshoq tarzda tozalanadi:
   device_hash bo'shatiladi, locked=False, allow_device_reset=True.
   Attempt'ning o'zi (in_progress) tegilmaydi — talaba qaytib davom ettira oladi.
        """,
        request_body=WrittenExamStatusUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Status muvaffaqiyatli yangilandi",
                examples={
                    "application/json": {
                        "message": "Imtihon statusi muvaffaqiyatli yangilandi"
                    }
                }
            ),
            400: "Noto‘g‘ri ma'lumot",
            403: "Ruxsat yo‘q",
            404: "Imtihon topilmadi",
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def patch(self, request, pk):
        try:
            exam = WrittenExam.objects.get(pk=pk)
        except WrittenExam.DoesNotExist:
            return Response(
                {
                    "message": "Imtihon topilmadi"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WrittenExamStatusUpdateSerializer(
            exam,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get("status", exam.status)

        # Faqat yoqilayotganda savollar yetarliligini tekshiramiz.
        # O'chirishga doim ruxsat — emergency vaziyatlar uchun.
        if new_status:
            counts = exam.questions.aggregate(
                easy=Count("id", filter=Q(difficulty="easy", status=True)),
                medium=Count("id", filter=Q(difficulty="medium", status=True)),
                hard=Count("id", filter=Q(difficulty="hard", status=True)),
            )

            if counts["easy"] < exam.easy_count:
                return Response({"message": "Oson savollar yetarli emas"}, status=400)

            if counts["medium"] < exam.medium_count:
                return Response({"message": "O‘rtacha savollar yetarli emas"}, status=400)

            if counts["hard"] < exam.hard_count:
                return Response({"message": "Qiyin savollar yetarli emas"}, status=400)

        with transaction.atomic():
            was_active = exam.status
            serializer.save()

            # Yoqilgan -> o'chirilgan o'tishida soft cleanup:
            # attempt'larga tegmaymiz (in_progress qoladi), faqat session'larni
            # tozalaymiz, shunda yangi qurilma bilan kirib davom ettirish mumkin.
            if was_active and not new_status:
                ExamSession.objects.filter(
                    attempt__exam=exam,
                    attempt__status="in_progress",
                ).update(
                    device_hash="",
                    locked=False,
                    allow_device_reset=True,
                )

        return Response(
            {
                "message": "Imtihon statusi muvaffaqiyatli yangilandi"
            },
            status=status.HTTP_200_OK
        )


class WrittenExamUpdateAPIView(APIView):
    """
    Yozma imtihonni qisman yangilash (PATCH)
    """
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Yozma imtihonni yangilash",
        operation_description="""
Admin tomonidan yozma imtihon ma'lumotlari qisman yangilanadi.

⚠️ Eslatma:
- Faqat yuborilgan maydonlar o‘zgartiriladi (partial update)
- Model darajasidagi validatsiyalar avtomatik ishlaydi
        """,
        request_body=BaseWrittenExamUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Imtihon muvaffaqiyatli yangilandi",
                examples={
                    "application/json": {
                        "message": "Imtihon muvaffaqiyatli yangilandi"
                    }
                }
            ),
            400: "Noto‘g‘ri ma'lumot yuborildi",
            403: "Ruxsat yo‘q",
            404: "Imtihon topilmadi"
        },
        tags=["Yangi yozma imtihonlar"]
    )
    def patch(self, request, pk):
        try:
            exam = WrittenExam.objects.get(pk=pk)
        except WrittenExam.DoesNotExist:
            return Response(
                {
                    "message": "Imtihon topilmadi"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if exam.status:
            return Response(
                {
                    "message": "Faol imtihonni yangilash mumkin emas"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BaseWrittenExamUpdateSerializer(
            exam,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Imtihon muvaffaqiyatli yangilandi"
            },
            status=status.HTTP_200_OK
        )


class WrittenExamListAPIView(ListAPIView):
    permission_classes = [IsAdmin, ]
    serializer_class = WrittenExamListSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = WrittenExamFilter

    queryset = WrittenExam.objects.select_related(
        "teacher__employee",
        "grader__employee",
        "subject",
        "curriculum",
        "created_by"
    ).order_by("-begin_time")

    @swagger_auto_schema(
        operation_summary="Yozma imtihonlar ro‘yxati",
        operation_description="""Admin uchun yozma imtihonlar ro‘yxatini olish endpointi. 
Turli xil filterlar orqali imtihonlarni saralash mumkin (masalan, fan, o'quv reja, o‘qituvchi, status va boshqalar       
            """,
        tags=["Yangi yozma imtihonlar"]

    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class WrittenExamDetailAPIView(RetrieveAPIView):
    permission_classes = [IsAdmin]
    serializer_class = WrittenExamDetailSerializer
    lookup_field = "pk"

    queryset = WrittenExam.objects.select_related(
        "teacher__employee",
        "grader__employee",
        "subject",
        "curriculum",
        "created_by"
    ).prefetch_related(
        "assigned_exams__group"
    )

    @swagger_auto_schema(
        operation_summary="Yozma imtihon batafsil ma’lumot",
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class WrittenExamDeleteAPIView(DestroyAPIView):
    permission_classes = [IsAdmin]
    lookup_field = "pk"
    queryset = WrittenExam.objects.all()

    @swagger_auto_schema(
        operation_summary="Yozma imtihonni o‘chirish",
        tags=["Yangi yozma imtihonlar"]
    )
    def delete(self, request, *args, **kwargs):

        exam = self.get_object()

        if exam.status:
            return Response(
                {"message": "Faol imtihonni o‘chirish mumkin emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        in_progress_exists = exam.attempts.filter(
            status="in_progress"
        ).exists()

        if in_progress_exists:
            return Response(
                {
                    "message": "Imtihon hozirda bajarilmoqda. O‘chirish mumkin emas."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        active_session_exists = ExamSession.objects.filter(
            attempt__exam=exam,
            status=True
        ).exists()

        if active_session_exists:
            return Response(
                {
                    "message": "Imtihon bo‘yicha faol sessiya mavjud. O‘chirish mumkin emas."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        exam.delete()

        return Response(
            {"message": "Imtihon muvaffaqiyatli o‘chirildi."},
            status=status.HTTP_200_OK
        )


class AssignGroupsToExamAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Imtihonga guruh(lar) biriktirish",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["exam_id", "group_ids"],
            properties={
                "exam_id": openapi.Schema(type=openapi.TYPE_STRING),
                "group_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING)
                )
            }
        ),
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request):
        exam_id = request.data.get("exam_id")
        group_ids = request.data.get("group_ids", [])

        # 1. validation
        if not group_ids:
            return Response(
                {"error": "Kamida bitta guruh yuborilishi kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            exam = WrittenExam.objects.get(pk=exam_id)
        except WrittenExam.DoesNotExist:
            return Response(
                {"error": "Imtihon topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        if exam.status:
            return Response(
                {"error": "Faol imtihonga guruh biriktirish mumkin emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. groups fetch (optimized)
        groups = list(Group.objects.filter(id__in=group_ids))

        if len(groups) != len(group_ids):
            return Response(
                {"error": "Ba’zi guruhlar topilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():

                # 🔒 lock groups (race condition fix)
                Group.objects.select_for_update().filter(id__in=group_ids)

                # 3. conflict check
                conflicts = WrittenExamGroup.objects.filter(
                    group__in=group_ids,
                    exam__curriculum=exam.curriculum,
                    exam__subject=exam.subject,
                    exam__exam_type=exam.exam_type,
                    exam__begin_time=exam.begin_time,
                )

                if conflicts.exists():
                    return Response(
                        {"error": "Ba’zi guruhlar uchun shu vaqtda imtihon mavjud"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 4. idempotency (skip already assigned)
                existing_group_ids = set(
                    WrittenExamGroup.objects.filter(
                        exam=exam,
                        group__in=group_ids
                    ).values_list('group_id', flat=True)
                )

                exam_group_objects = [
                    WrittenExamGroup(exam=exam, group=g)
                    for g in groups if g.id not in existing_group_ids
                ]

                if exam_group_objects:
                    WrittenExamGroup.objects.bulk_create(exam_group_objects)

                # 5. student access (optimized)
                student_ids = Student.objects.filter(
                    group_id__in=group_ids
                ).values_list('id', flat=True)

                access_objects = [
                    WrittenExamAccess(
                        exam=exam,
                        student_id=sid,
                        is_accessible=True
                    )
                    for sid in student_ids
                ]

                if access_objects:
                    WrittenExamAccess.objects.bulk_create(access_objects)

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Guruhlar muvaffaqiyatli biriktirildi."},
            status=status.HTTP_201_CREATED
        )


class RemoveGroupFromExamAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Imtihondan guruhni olib tashlash",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["exam_id", "group_id"],
            properties={
                "exam_id": openapi.Schema(type=openapi.TYPE_STRING),
                "group_id": openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Yangi yozma imtihonlar"]
    )
    def delete(self, request):

        exam_id = request.data.get("exam_id")
        group_id = request.data.get("group_id")

        try:
            exam = WrittenExam.objects.get(pk=exam_id)
        except WrittenExam.DoesNotExist:
            return Response(
                {
                    "error": "Imtihon topilmadi"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(
                {
                    "error": "Guruh topilmadi"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if exam.status:
            return Response(
                {"error": "Faol imtihondan guruhni olib tashlash mumkin emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            WrittenExamGroup.objects.filter(
                exam=exam,
                group=group
            ).delete()

            students = Student.objects.filter(group=group).only("id")

            WrittenExamAccess.objects.filter(
                exam=exam,
                student__in=students
            ).delete()

        return Response(
            {"message": "Guruh imtihondan olib tashlandi."},
            status=status.HTTP_200_OK
        )


class ExamAccessStudentListAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Imtihon va guruh bo‘yicha talabalar ro‘yxati",
        manual_parameters=[
            openapi.Parameter(
                "exam_id",
                openapi.IN_QUERY,
                description="Imtihon ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                "group_id",
                openapi.IN_QUERY,
                description="Guruh ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request):

        exam_id = request.query_params.get("exam_id")
        group_id = request.query_params.get("group_id")

        try:
            exam = WrittenExam.objects.get(pk=exam_id)
        except WrittenExam.DoesNotExist:
            return Response(
                {"error": "Imtihon topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(
                {"error": "Guruh topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        access_qs = WrittenExamAccess.objects.select_related("student").filter(
            exam=exam,
            student__group=group
        )

        data = [
            {
                "id": access.student.id,
                "name": access.student.full_name,
                "is_accessible": access.is_accessible
            }
            for access in access_qs
        ]

        return Response(data, status=status.HTTP_200_OK)


class UpdateExamAccessStatusAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Talabaning imtihonga kirish statusini o‘zgartirish",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["exam_id", "student_id", "is_accessible"],
            properties={
                "exam_id": openapi.Schema(type=openapi.TYPE_STRING),
                "student_id": openapi.Schema(type=openapi.TYPE_STRING),
                "is_accessible": openapi.Schema(type=openapi.TYPE_BOOLEAN)
            }
        ),
        tags=["Yangi yozma imtihonlar"]
    )
    def patch(self, request):

        exam_id = request.data.get("exam_id")
        student_id = request.data.get("student_id")
        is_accessible = request.data.get("is_accessible")

        if is_accessible is None:
            return Response(
                {"error": "status yuborish majburiy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():

                access = (
                    WrittenExamAccess.objects
                    .select_for_update()
                    .select_related("exam")
                    .get(exam_id=exam_id, student_id=student_id)
                )

                # Live rejimda (exam.status=True) talaba imtihon ichida bo'lsa
                # statusni o'zgartirishga ruxsat bermaymiz.
                # Maintenance rejimda (exam.status=False) admin bemalol o'zgartiradi.
                if access.exam.status:
                    in_progress_exists = WrittenExamAttempt.objects.filter(
                        exam_id=exam_id,
                        student_id=student_id,
                        status="in_progress"
                    ).exists()

                    if in_progress_exists:
                        return Response(
                            {
                                "error": "Talaba hozirda imtihonni bajarmoqda. "
                                         "Avval imtihonni vaqtincha o'chiring "
                                         "(WrittenExamStatusUpdate orqali status=False)."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                access.is_accessible = is_accessible
                access.save(update_fields=["is_accessible"])

        except WrittenExamAccess.DoesNotExist:
            return Response(
                {"error": "Talaba ushbu imtihon uchun topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": "Talaba statusi muvaffaqiyatli yangilandi"},
            status=status.HTTP_200_OK
        )


class AdminExamGroupStatsAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Imtihon bo‘yicha guruhlar statistikasi",
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id):
        groups = (
            WrittenExamGroup.objects
            .filter(exam_id=exam_id)
            .select_related("group")
        )

        result = []

        for g in groups:
            students = Student.objects.filter(group=g.group)

            attempts = WrittenExamAttempt.objects.filter(
                exam_id=exam_id,
                student__group=g.group
            ).order_by("student_id", "-attempt_no").distinct("student_id")

            submitted = attempts.filter(status="submitted").count()

            graded = (
                WrittenExamAnswer.objects
                .filter(
                    attempt__in=attempts,
                    score__isnull=False
                )
                .values("attempt")
                .distinct()
                .count()
            )

            result.append({
                "group_id": g.group.id,
                "group_name": g.group.name,
                "students_total": students.count(),
                "submitted": submitted,
                "graded": graded
            })

        return Response(result)
# class AdminExamGroupStatsAPIView(APIView):
#     permission_classes = [IsAdmin]
#
#     @swagger_auto_schema(
#         operation_summary="Imtihon bo‘yicha guruhlar statistikasi",
#         tags=["Yangi yozma imtihonlar"]
#     )
#     def get(self, request, exam_id):
#
#         groups = (
#             WrittenExamGroup.objects
#             .filter(exam_id=exam_id)
#             .select_related("group")
#         )
#
#         group_ids = [g.group_id for g in groups]
#
#         students_count = dict(
#             Student.objects
#             .filter(group_id__in=group_ids)
#             .values("group_id")
#             .annotate(total=Count("id"))
#             .values_list("group_id", "total")
#         )
#
#         attempts = (
#             WrittenExamAttempt.objects
#             .filter(exam_id=exam_id, student__group_id__in=group_ids)
#             .order_by("student_id", "-attempt_no")
#             .distinct("student_id")
#         )
#
#         submitted_count = dict(
#             attempts
#             .filter(status="submitted")
#             .values("student__group_id")
#             .annotate(total=Count("id"))
#             .values_list("student__group_id", "total")
#         )
#
#         graded_count = dict(
#             WrittenExamAnswer.objects
#             .filter(
#                 attempt__in=attempts,
#                 score__isnull=False
#             )
#             .values("attempt__student__group_id")
#             .annotate(total=Count("attempt", distinct=True))
#             .values_list("attempt__student__group_id", "total")
#         )
#
#         result = []
#
#         for g in groups:
#             gid = g.group_id
#
#             result.append({
#                 "group_id": gid,
#                 "group_name": g.group.name,
#                 "students_total": students_count.get(gid, 0),
#                 "submitted": submitted_count.get(gid, 0),
#                 "graded": graded_count.get(gid, 0),
#             })
#
#         return Response(result)

class AdminExamGroupStudentsAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Guruh bo‘yicha talabalar natijalari",
        tags=["Admin Exam"]
    )
    def get(self, request, exam_id, group_id):

        students = Student.objects.filter(group_id=group_id).select_related("user")

        result = []

        for student in students:

            access = WrittenExamAccess.objects.filter(
                exam_id=exam_id,
                student=student,
                is_accessible=True
            ).exists()

            if not access:
                result.append({
                    "student_id": student.id,
                    "name": student.full_name,
                    "message": "Ruxsat berilmagan"
                })
                continue

            attempt = (
                WrittenExamAttempt.objects
                .filter(
                    exam_id=exam_id,
                    student=student
                )
                .order_by("-attempt_no")
                .first()
            )

            if not attempt:
                result.append({
                    "student_id": student.id,
                    "name": student.full_name,
                    "message": "Topshirmagan"
                })
                continue

            score = (
                WrittenExamAnswer.objects
                .filter(attempt=attempt)
                .aggregate(total=Sum("score"))["total"]
            )

            result.append({
                "student_id": student.id,
                "name": student.full_name,
                "status": attempt.status,
                "score": score,
                "message": "Baholanmagan" if score is None else None
            })

        return Response(result)


class ExamQuestionShow(APIView):
    permission_classes = [IsAdmin]
    pagination_class = CustomQPageNumberPagination

    @swagger_auto_schema(
        operation_summary="Imtihon savollarini olish",
        tags=["Yangi yozma imtihonlar"],
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("page_size", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        responses={200: WrittenExamQuestionSerializer(many=True)}
    )
    def get(self, request, exam_id):
        queryset = (
            WrittenExamQuestion.objects
            .filter(exam_id=exam_id)
            .select_related("question_bank", "exam")
        )

        difficulty_stats = (
            queryset
            .values("difficulty")
            .annotate(count=Count("id"))
        )

        difficulty_counts = {i["difficulty"]: i["count"] for i in difficulty_stats}

        paginator = self.pagination_class()
        paginator.difficulty_counts = difficulty_counts

        page = paginator.paginate_queryset(queryset, request)

        serializer = WrittenExamQuestionSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

class ExamResultAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Imtihon natijalari (oxirgi urinish bo‘yicha)",
        manual_parameters=[
            openapi.Parameter(
                'exam_id',
                openapi.IN_PATH,
                description="Imtihon ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id):

        # 1. exam check
        try:
            exam = WrittenExam.objects.get(pk=exam_id)
        except WrittenExam.DoesNotExist:
            raise NotFound("Imtihon topilmadi")

        # 2. students (examga biriktirilgan guruhlar orqali)
        students = (
            Student.objects
            .filter(group__exam_assignments__exam=exam)
            .select_related("group")
            .distinct()
        )

        # 🔥 3. faqat yakunlangan oxirgi attempt
        latest_attempt = (
            WrittenExamAttempt.objects
            .filter(
                exam=exam,
                student=OuterRef("pk"),
                status__in=["submitted", "expired"]  # 🔥 MUHIM
            )
            .order_by("-attempt_no")
        )

        # 🔥 4. annotate
        students = students.annotate(
            last_attempt_no=Subquery(latest_attempt.values("attempt_no")[:1]),
            last_attempt_status=Subquery(latest_attempt.values("status")[:1]),
            last_attempt_score=Subquery(
                latest_attempt.annotate(
                    total=Sum("answers__score")
                ).values("total")[:1]
            )
        )

        # 5. response
        result = [
            {
                "student_id": s.id,
                "full_name": s.full_name,
                "group": s.group.name if s.group else None,
                "attempt_no": s.last_attempt_no,   # 🔥 asosiy o‘zgarish
                "status": s.last_attempt_status,
                "score": float(s.last_attempt_score or 0),
                "has_attempt": s.last_attempt_no is not None  # 🔥 optional
            }
            for s in students
        ]

        return Response(result, status=status.HTTP_200_OK)

class ExamLogsAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Imtihon loglari (IP, vaqtlar, urinishlar)",
        manual_parameters=[
            openapi.Parameter(
                'exam_id',
                openapi.IN_PATH,
                description="Imtihon ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id):

        try:
            exam = WrittenExam.objects.get(pk=exam_id)
        except WrittenExam.DoesNotExist:
            raise NotFound("Imtihon topilmadi")

        groups = (
            Group.objects
            .filter(exam_assignments__exam=exam)
            .prefetch_related(
                Prefetch(
                    "student_group",   # ✅ to‘g‘ri related_name
                    queryset=Student.objects.prefetch_related(
                        Prefetch(
                            "exam_attempts",
                            queryset=WrittenExamAttempt.objects
                            .filter(exam=exam)
                            .order_by("-attempt_no")
                        )
                    )
                )
            )
            .distinct()
        )

        result = []

        for g in groups:
            group_data = {
                "group_id": g.id,
                "group_name": g.name,
                "students": []
            }

            for student in g.student_group.all():   # ✅ to‘g‘ri access

                attempts = student.exam_attempts.all()

                student_data = {
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "attempts": [
                        {
                            "attempt_no": a.attempt_no,
                            "status": a.status,
                            "ip_address": a.ip_address,
                            "started_at": a.started_at,
                            "submitted_at": a.submitted_at,
                            "expires_at": a.expires_at,
                        }
                        for a in attempts
                    ]
                }

                group_data["students"].append(student_data)

            result.append(group_data)

        return Response(result,status=status.HTTP_200_OK)

class AdminResetStudentExamDeviceAPIView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Talaba qurilmasini reset qilish",
        manual_parameters=[
            openapi.Parameter(
                "exam_id",
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                "student_id",
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request,exam_id,student_id):

        if not exam_id or not student_id:
            raise ValidationError("exam_id va student_id majburiy")

        try:
            exam = WrittenExam.objects.get(pk=exam_id)
        except WrittenExam.DoesNotExist:
            raise NotFound("Imtihon topilmadi")

        # 🔥 1. oxirgi attempt
        attempt = (
            WrittenExamAttempt.objects
            .filter(
                exam_id=exam_id,
                student_id=student_id
            )
            .order_by("-attempt_no")
            .first()
        )

        if not attempt:
            raise NotFound("Attempt topilmadi")

        # Live rejimda (exam.status=True) faqat in_progress attemptni reset qilamiz.
        # Maintenance rejimda (exam.status=False) admin har qanday holatda reset qila oladi
        # (terminated, expired, submitted) — emergency uchun.
        if exam.status and attempt.status != "in_progress":
            return Response({
                "error": f"Attempt holati: {attempt.status}, reset qilib bo‘lmaydi. "
                         f"Avval imtihonni vaqtincha o'chiring (status=False)."
            }, status=400)

        # 🔥 2. session
        try:
            session = ExamSession.objects.get(attempt=attempt)
        except ExamSession.DoesNotExist:
            raise NotFound("Session topilmadi")

        # 🔥 3. RESET LOGIC
        session.device_hash = ""
        session.allow_device_reset = True
        session.locked = False
        session.save(update_fields=[
            "device_hash",
            "allow_device_reset",
            "locked"
        ])

        # 🔥 4. attempt ham tozalaymiz (optional)
        attempt.device_fingerprint = None
        attempt.ip_address = None
        attempt.save(update_fields=["device_fingerprint", "ip_address"])

        return Response({
            "message": "Qurilma reset qilindi",
            "attempt_id": attempt.id,
            "attempt_no": attempt.attempt_no
        }, status=status.HTTP_200_OK)