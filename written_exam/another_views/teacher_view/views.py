from decimal import Decimal

from django.db import transaction
from django.db.models import Count
from django.db.models import OuterRef
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import Sum
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsAdminOrTeacher
from shared.permissions import IsTeacher
from shared.utils import CustomPageNumberPagination
from written_exam.another_views.teacher_view.serializers import AttemptDetailSerializer
from written_exam.another_views.teacher_view.serializers import BaseQuestionSerializer
from written_exam.another_views.teacher_view.serializers import ExamGroupSerializer
from written_exam.another_views.teacher_view.serializers import ExamResultSerializer
from written_exam.another_views.teacher_view.serializers import GradeAnswerSerializer
from written_exam.another_views.teacher_view.serializers import QuestionCollectionSerializer
from written_exam.another_views.teacher_view.serializers import TeacherExamListSerializer
from written_exam.another_views.teacher_view.serializers import WrittenExamQuestionListSerializer
from written_exam.models import AttemptQuestion
from written_exam.models import QuestionBank
from written_exam.models import QuestionCollection
from written_exam.models import WrittenExam
from written_exam.models import WrittenExamAnswer
from written_exam.models import WrittenExamAttempt
from written_exam.models import WrittenExamGroup
from written_exam.models import WrittenExamQuestion


class QuestionCollectionCreateAPIView(APIView):
    permission_classes = [IsTeacher, ]

    @swagger_auto_schema(
        operation_summary="Savol bazasi yaratish",
        request_body=QuestionCollectionSerializer,
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request):
        serializer = QuestionCollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(
            {
                "message": "Savol bazasi muvaffaqiyatli yaratildi",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)


class QuestionCollectionListAPIView(APIView):
    permission_classes = [IsTeacher, ]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_summary="Savol bazalari ro‘yxati",
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request):
        qs = QuestionCollection.objects.filter(
            created_by=request.user,
            is_deleted=False
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)

        serializer = QuestionCollectionSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class QuestionCollectionUpdateAPIView(APIView):
    permission_classes = [IsTeacher, ]

    @swagger_auto_schema(
        operation_summary="Savol bazasini yangilash",
        request_body=QuestionCollectionSerializer,
        tags=["Yangi yozma imtihonlar"]
    )
    def patch(self, request, pk):

        try:
            collection = QuestionCollection.objects.get(pk=pk, created_by=request.user, is_deleted=False)
        except QuestionCollection.DoesNotExist:
            return Response(
                {"error": "Savol bazasi topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QuestionCollectionSerializer(
            collection,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Savol bazasi muvaffaqiyatli yangilandi",
                "data": serializer.data
            }
        )


class QuestionCollectionDeleteAPIView(APIView):
    permission_classes = [IsTeacher, ]

    @swagger_auto_schema(
        operation_summary="Savol bazasini o‘chirish (soft delete)",
        tags=["Yangi yozma imtihonlar"]
    )
    def delete(self, request, pk):
        try:
            collection = QuestionCollection.objects.get(pk=pk, created_by=request.user)
        except QuestionCollection.DoesNotExist:
            return Response(
                {"error": "Savol bazasi topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        collection.is_deleted = True
        collection.save(update_fields=["is_deleted"])

        return Response(
            {"message": "Savol bazasi o‘chirildi"},
            status=status.HTTP_200_OK
        )


class QuestionCreateAPIView(APIView):
    permission_classes = [IsTeacher, ]

    @swagger_auto_schema(
        operation_summary="Savol yaratish",
        request_body=BaseQuestionSerializer,
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request):
        serializer = BaseQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        collection = serializer.validated_data["collection"]

        if collection.created_by != request.user:
            return Response(
                {"error": "Sizga ushbu savol bazasiga savol qo‘shish huquqi berilmagan"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save()
        return Response(
            {
                "message": "Savol muvaffaqiyatli yaratildi",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)


class QuestionListAPIView(APIView):
    permission_classes = [IsTeacher]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_summary="Savollar ro‘yxati",
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request):
        collection_id = request.query_params.get("collection")

        qs = QuestionBank.objects.filter(
            collection__created_by=request.user,
            is_deleted=False
        )

        if collection_id:
            qs = qs.filter(collection_id=collection_id)

        qs = qs.order_by("-created_at")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)

        serializer = BaseQuestionSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class QuestionUpdateAPIView(APIView):
    permission_classes = [IsTeacher, ]

    @swagger_auto_schema(
        operation_summary="Savolni yangilash",
        request_body=BaseQuestionSerializer,
        tags=["Yangi yozma imtihonlar"]
    )
    def patch(self, request, pk):

        try:
            question = QuestionBank.objects.get(pk=pk, collection__created_by=request.user, is_deleted=False)
        except QuestionBank.DoesNotExist:
            return Response(
                {"error": "Savol topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )
        if question.exam_usages.exists():
            return Response(
                {"error": "Savol imtihonda ishlatilgan. Tahrirlash mumkin emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BaseQuestionSerializer(
            question,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Savol muvaffaqiyatli yangilandi",
                "data": serializer.data
            }
        )


class QuestionDeleteAPIView(APIView):
    permission_classes = [IsTeacher, ]

    @swagger_auto_schema(
        operation_summary="Savolni o‘chirish (soft delete)",
        tags=["Yangi yozma imtihonlar"]
    )
    def delete(self, request, pk):
        try:
            question = QuestionBank.objects.get(pk=pk, collection__created_by=request.user)
        except QuestionBank.DoesNotExist:
            return Response(
                {"error": "Savol topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )
        if question.exam_usages.exists():
            return Response(
                {"error": "Savol imtihonda ishlatilgan. O‘chirib bo‘lmaydi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        question.is_deleted = True
        question.save(update_fields=["is_deleted"])

        return Response(
            {"message": "Savol o‘chirildi"},
            status=status.HTTP_200_OK
        )


class QuestionDetailAPIView(APIView):
    permission_classes = [IsTeacher, ]

    @swagger_auto_schema(
        operation_summary="Savolni ko‘rish",
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, pk):
        try:
            question = QuestionBank.objects.select_related(
                "collection"
            ).get(
                pk=pk,
                collection__created_by=request.user,
                is_deleted=False
            )
        except QuestionBank.DoesNotExist:
            return Response(
                {"error": "Savol topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BaseQuestionSerializer(question)
        return Response(
            {
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class TeacherExamListAPIView(ListAPIView):
    permission_classes = [IsTeacher]
    serializer_class = TeacherExamListSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user

        return (
            WrittenExam.objects
            .filter(
                Q(teacher=user) | Q(grader=user)   # 🔥 asosiy fix
            )
            .select_related(
                "subject",
                "curriculum",
                "teacher",
                "grader"
            )
            .prefetch_related(
                "assigned_exams__group"
            )
            .order_by("-created_at")
        )

    @swagger_auto_schema(
        operation_summary="O‘qituvchiga biriktirilgan imtihonlar ro‘yxati",
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class TeacherExamQuestionRequirementAPIView(APIView):
    permission_classes = [IsTeacher]

    @swagger_auto_schema(
        operation_summary="Imtihon savol talablari va holati",
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id):
        try:
            exam = WrittenExam.objects.select_related(
                "subject",
                "curriculum",
                "teacher",
                "grader",
            ).get(pk=exam_id, teacher=request.user)
        except WrittenExam.DoesNotExist:
            return Response({"error": "Imtihon topilmadi"}, status=404)

        current_qs = exam.questions.values("difficulty").annotate(
            count=Count("id")
        )
        current_map = {item["difficulty"]: item["count"] for item in current_qs}

        current_easy = current_map.get("easy", 0)
        current_medium = current_map.get("medium", 0)
        current_hard = current_map.get("hard", 0)

        # Remaining (minus chiqmasligi uchun max bilan o‘ramiz)
        remaining_easy = max(exam.easy_count - current_easy, 0)
        remaining_medium = max(exam.medium_count - current_medium, 0)
        remaining_hard = max(exam.hard_count - current_hard, 0)

        # Teacher available pool
        teacher_qs = QuestionBank.objects.filter(
            collection__created_by=request.user,
            is_deleted=False,
            status=True
        ).values("difficulty").annotate(
            count=Count("id")
        )
        teacher_map = {item["difficulty"]: item["count"] for item in teacher_qs}

        teacher_easy = teacher_map.get("easy", 0)
        teacher_medium = teacher_map.get("medium", 0)
        teacher_hard = teacher_map.get("hard", 0)

        response = {
            "exam": {
                "id": exam.id,
                "name": exam.name,
                "description": exam.description,
                "exam_type": exam.exam_type,
                "subject": exam.subject.name if exam.subject else None,
                "curriculum": exam.curriculum.name if exam.curriculum else None,
                "teacher": exam.teacher.full_name if hasattr(exam.teacher, "full_name") else exam.teacher.id,
                "grader": exam.grader.full_name if hasattr(exam.grader, "full_name") else exam.grader.id,
                "begin_time": exam.begin_time,
                "end_time": exam.end_time,
                "duration_minutes": exam.duration_minutes,
                "max_score": exam.max_score,
                "status": exam.status,
                "total_required": exam.total_questions,
                "is_editable": exam.is_editable,
            },
            "distribution": {
                "required": {
                    "easy": exam.easy_count,
                    "medium": exam.medium_count,
                    "hard": exam.hard_count,
                },
                "current": {
                    "easy": current_easy,
                    "medium": current_medium,
                    "hard": current_hard,
                },
                "remaining": {
                    "easy": remaining_easy,
                    "medium": remaining_medium,
                    "hard": remaining_hard,
                },
                "teacher_available": {
                    "easy": teacher_easy,
                    "medium": teacher_medium,
                    "hard": teacher_hard,
                }
            }
        }

        return Response(response, status=200)


class TeacherExamAddQuestionsAPIView(APIView):
    permission_classes = [IsTeacher]

    @swagger_auto_schema(
        operation_summary="Imtihonga savol qo‘shish",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["question_ids"],
            properties={
                "question_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING)
                )
            },
        ),
        tags=["Yangi yozma imtihonlar"]
    )
    def post(self, request, exam_id):

        question_ids = request.data.get("question_ids", [])

        if not question_ids or not isinstance(question_ids, list):
            return Response(
                {"error": "question_ids ro‘yxat bo‘lishi kerak"},
                status=400
            )

        question_ids = list(set(question_ids))

        with transaction.atomic():

            try:
                exam = WrittenExam.objects.select_for_update().get(
                    pk=exam_id,
                    teacher=request.user
                )
            except WrittenExam.DoesNotExist:
                return Response({"error": "Imtihon topilmadi"}, status=404)

            now = timezone.now()

            if exam.status:
                return Response({"error": "Active imtihonga savol qo‘shib bo‘lmaydi"}, status=400)

            if exam.begin_time <= now:
                return Response({"error": "Boshlangan imtihonga savol qo‘shib bo‘lmaydi"}, status=400)

            if exam.end_time <= now:
                return Response({"error": "Tugagan imtihonga savol qo‘shib bo‘lmaydi"}, status=400)

            if exam.attempts.exists():
                return Response({"error": "Imtihon jarayoni boshlangan"}, status=400)

            questions = QuestionBank.objects.filter(
                id__in=question_ids,
                collection__created_by=request.user,
                is_deleted=False,
                status=True
            )

            valid_ids = set(questions.values_list("id", flat=True))
            invalid_ids = set(question_ids) - valid_ids

            existing_ids = set(
                exam.questions.filter(
                    question_bank_id__in=valid_ids
                ).values_list("question_bank_id", flat=True)
            )

            to_add = questions.exclude(id__in=existing_ids)

            new_objects = [
                WrittenExamQuestion(
                    exam=exam,
                    question_bank=q,
                    text=q.text,
                    difficulty=q.difficulty,
                    status=True
                )
                for q in to_add
            ]

            if new_objects:
                WrittenExamQuestion.objects.bulk_create(new_objects)

        return Response({
            "added_count": len(new_objects),
            "skipped_existing": list(existing_ids),
            "invalid_ids": list(invalid_ids),
        }, status=201)


class WrittenExamQuestionListAPIView(APIView):
    permission_classes = [IsAdminOrTeacher, ]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_summary="Imtihonga tegishli savollar ro‘yxati",
        operation_description="O‘qituvchi o‘z imtihoniga tegishli savollarni ko‘radi (pagination bilan)",
        tags=["Yangi yozma imtihonlar"],
        manual_parameters=[
            openapi.Parameter(
                'exam_id',
                openapi.IN_QUERY,
                description="Imtihon ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Sahifa raqami",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Har sahifadagi elementlar soni",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: WrittenExamQuestionListSerializer(many=True),
            400: "exam_id kiritilmagan",
            403: "Ruxsat yo‘q",
            404: "Imtihon topilmadi"
        }
    )
    def get(self, request):
        exam_id = request.query_params.get("exam_id")

        if not exam_id:
            return Response(
                {"error": "exam_id kiritilishi shart"},
                status=400
            )

        try:
            exam = WrittenExam.objects.get(id=exam_id)
        except WrittenExam.DoesNotExist:
            raise NotFound("Imtihon topilmadi")

        queryset = (
            WrittenExamQuestion.objects
            .filter(exam=exam, status=True)
            .only("id", "text", "difficulty", "status")
            .order_by("id")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = WrittenExamQuestionListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class WrittenExamQuestionDeleteAPIView(APIView):
    permission_classes = [IsTeacher]

    @swagger_auto_schema(
        operation_summary="Imtihondan savolni o‘chirish",
        operation_description="O‘qituvchi o‘z imtihoniga tegishli savolni o‘chiradi",
        tags=["Yangi yozma imtihonlar"],
        responses={
            204: "Savol muvaffaqiyatli o‘chirildi",
            403: "Ruxsat yo‘q",
            404: "Topilmadi"
        }
    )
    def delete(self, request, exam_id, question_id):

        try:
            question = (
                WrittenExamQuestion.objects
                .select_related("exam")
                .get(id=question_id, exam_id=exam_id)
            )
        except WrittenExamQuestion.DoesNotExist:
            raise NotFound("Savol topilmadi")

        exam = question.exam

        if exam.teacher != request.user:
            raise PermissionDenied("Siz bu imtihonni boshqara olmaysiz")

        from django.utils import timezone
        if exam.begin_time <= timezone.now():
            raise ValidationError("Boshlangan imtihondan savolni o‘chirib bo‘lmaydi")

        if exam.attempts.exists():
            raise ValidationError("Talabalar urinish boshlagan. Savolni o‘chirib bo‘lmaydi")

        question.delete()

        return Response(
            data={
                "message": "Savol muvaffaqiyatli o‘chirildi"
            },
            status=200,
        )


class ExamResultsAPIView(APIView):
    permission_classes = [IsTeacher]
    serializer_class = ExamResultSerializer
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_summary="Imtihon natijalarini chiqarish",
        operation_description="Talaba ismi va guruh bo‘yicha filterlash mumkin",
        tags=["Yangi yozma imtihonlar"],
        responses={
            200: ExamResultSerializer(many=True),
            403: "Ruxsat yo‘q",
            404: "Topilmadi"
        }
    )
    def get(self, request, exam_id):

        search = request.query_params.get("search")
        group_id = request.query_params.get("group")

        try:
            exam = WrittenExam.objects.get(id=exam_id)
        except WrittenExam.DoesNotExist:
            raise NotFound("Imtihon topilmadi")

        # 🔥 ASOSIY CHECK
        if exam.grader != request.user:
            return Response([],status=status.HTTP_200_OK)  # ❗ bo‘sh qaytadi

        # har bir student uchun oxirgi attempt id
        last_attempt = (
            WrittenExamAttempt.objects
            .filter(
                exam=exam,
                student_id=OuterRef("student_id")
            )
            .order_by("-attempt_no")
            .values("id")[:1]
        )

        attempts = (
            WrittenExamAttempt.objects
            .filter(
                id=Subquery(last_attempt),
                status__in=["submitted", "expired"]
            )
            .select_related("student", "student__group")
            .annotate(
                total_score_db=Sum("answers__score")
            )
        )

        if search:
            attempts = attempts.filter(
                Q(student__first_name__icontains=search) |
                Q(student__second_name__icontains=search) |
                Q(student__third_name__icontains=search) |
                Q(student__full_name__icontains=search)
            )

        if group_id:
            attempts = attempts.filter(student__group_id=group_id)

        attempts = attempts.order_by("-started_at")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(attempts, request, view=self)

        serializer = self.serializer_class(page, many=True)

        return paginator.get_paginated_response(serializer.data)

class ExamStudentLastAttemptAPIView(APIView):
    permission_classes = [IsTeacher]

    @swagger_auto_schema(
        operation_summary="Talabaning oxirgi imtihon javoblari",
        operation_description="Exam ID va Student ID orqali talabaning oxirgi attempt savollari va javoblarini olish",
        tags=["Yangi yozma imtihonlar"],
        responses={
            200: AttemptDetailSerializer,
            403: "Ruxsat yo‘q",
            404: "Attempt topilmadi"
        }
    )
    def get(self, request, exam_id, student_id):
        attempt = (
            WrittenExamAttempt.objects
            .filter(
                exam_id=exam_id,
                student_id=student_id,
                status__in=["submitted", "expired"]
            )
            .select_related("student")
            .prefetch_related(
                "questions__question",
                "answers"
            )
            .order_by("-attempt_no")
            .first()
        )

        if not attempt:
            raise NotFound("Attempt topilmadi")

        attempt = (
            WrittenExamAttempt.objects
            .filter(id=attempt.id)
            .select_related("student")
            .prefetch_related(
                Prefetch(
                    "questions",
                    queryset=AttemptQuestion.objects
                    .select_related("question")
                    .prefetch_related("question__answers")
                    .order_by("order")
                )
            )
            .first()
        )

        serializer = AttemptDetailSerializer(attempt)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GradeAttemptAPIView(APIView):
    permission_classes = [IsTeacher]

    @swagger_auto_schema(
        operation_summary="Savolga ball qo‘yish",
        request_body=GradeAnswerSerializer,
        tags=["Yangi yozma imtihonlar"],
        responses={
            200: "Ball qo‘yildi",
            400: "Ball limitdan oshdi",
            404: "Attempt topilmadi"
        }
    )
    def post(self, request):

        serializer = GradeAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exam_id = serializer.validated_data["exam_id"]
        student_id = serializer.validated_data["student_id"]
        question_id = serializer.validated_data["question_id"]
        score = serializer.validated_data["score"]
        comment = serializer.validated_data.get("comment")

        attempt = (
            WrittenExamAttempt.objects
            .filter(
                exam_id=exam_id,
                student_id=student_id,
                status__in=["submitted", "expired"]
            )
            .select_related("exam")
            .order_by("-attempt_no")
            .first()
        )

        if not attempt:
            raise NotFound("Attempt topilmadi")

        try:
            answer = (
                WrittenExamAnswer.objects
                .select_related("question")
                .get(attempt=attempt, question_id=question_id)
            )
        except WrittenExamAnswer.DoesNotExist:
            raise NotFound("Javob topilmadi")

        if answer.score is not None:
            raise ValidationError({"error": "Bu savolga allaqachon ball qo‘yilgan"})

        exam = attempt.exam
        difficulty = answer.question.difficulty

        # 🔥 per-question max
        if difficulty == "easy":
            max_q_score = exam.easy_total_score / exam.easy_count if exam.easy_count else Decimal("0")
        elif difficulty == "medium":
            max_q_score = exam.medium_total_score / exam.medium_count if exam.medium_count else Decimal("0")
        else:
            max_q_score = exam.hard_total_score / exam.hard_count if exam.hard_count else Decimal("0")

        # ❗ 1. per-question validation
        if score < 0:
            raise ValidationError({"score": "Ball manfiy bo‘lmasin"})

        if score > max_q_score:
            raise ValidationError({
                "score": f"Bu savol uchun maksimal ball: {max_q_score}"
            })

        # 🔥 global max
        max_score = (
            exam.easy_total_score +
            exam.medium_total_score +
            exam.hard_total_score
        )

        # ❗ SAVE QILMASDAN OLDIN hisoblaymiz
        used_score = (
            WrittenExamAnswer.objects
            .filter(attempt=attempt)
            .exclude(pk=answer.pk)
            .aggregate(total=Sum("score"))["total"]
            or Decimal("0.00")
        )

        total_after = used_score + score

        # ❗ 2. global validation
        if total_after > max_score:
            raise ValidationError({
                "total": f"Jami ball oshib ketadi. Qolgan: {max_score - used_score}"
            })

        # ✅ HAMMASI OK → endi save
        with transaction.atomic():

            answer.score = score
            answer.comment = comment
            answer.save(update_fields=["score", "comment"])

            if attempt.is_fully_graded:
                attempt.graded_at = timezone.now()
                attempt.save(update_fields=["graded_at"])

        return Response({
            "message": "Ball saqlandi",
            "question_max_score": max_q_score,
            "total_score": total_after,
            "max_score": max_score
        })

class ExamGroupsAPIView(APIView):
    permission_classes = [IsTeacher]

    @swagger_auto_schema(
        operation_summary="Imtihonga tegishli guruhlar",
        responses={200: ExamGroupSerializer(many=True)},
        tags=["Yangi yozma imtihonlar"]
    )
    def get(self, request, exam_id):

        try:
            WrittenExam.objects.only("id").get(id=exam_id)
        except WrittenExam.DoesNotExist:
            raise NotFound("Imtihon topilmadi")

        groups = (
            WrittenExamGroup.objects
            .filter(exam_id=exam_id)
            .select_related("group")
            .values(
                "group__id",
                "group__name"
            )
        )

        data = [
            {
                "id": g["group__id"],
                "name": g["group__name"]
            }
            for g in groups
        ]

        return Response(data)
