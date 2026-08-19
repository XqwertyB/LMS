from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models import QuerySet

from content.models import Task_students
from shared.utils import CustomPageNumberPagination
from students.models import Student
from students.serializers import StudentForGroupSerializer
from subjects.models import Subject_Curriculum
from user.permission import IsAdmin
from .models import ConnectGrades, Grade
from .serializer import (
    Subject_GradesSerializer, CreateGradeSerializer, ConnectGradeListSerializer, GradeDetailSerializer, )

from drf_yasg.utils import swagger_auto_schema

from .services import GradeService, calculate_on, calculate_yn


class SubjectCurriculumListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_summary="Curriculum va Semester bo‘yicha fanlar ro'yxati",
        tags=["Vedmost"]
    )
    def get(self, request):

        curriculum_id = request.GET.get("curriculum_id")
        semester_id = request.GET.get("semester_id")

        queryset: QuerySet = (
            Subject_Curriculum.objects
            .select_related(
                "subject",
                "subject_semestr",
                "subject_curriculum"
            )
            .order_by("id")
        )

        if curriculum_id:
            queryset = queryset.filter(subject_curriculum_id=curriculum_id)

        if semester_id:
            queryset = queryset.filter(subject_semestr_id=semester_id)

        # ✅ pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = Subject_GradesSerializer(page, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "data": serializer.data,
            "message": "success"
        })

class CreateGradeSheetView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Vedomost yaratish",
        request_body=CreateGradeSerializer,
        responses={
            201: openapi.Response(
                description="Yaratildi",
                examples={
                    "application/json": {
                        "success": True,
                        "connect_id": "uuid"
                    }
                }
            )
        },
        tags=["Vedmost"]
    )
    def post(self, request):
        s = CreateGradeSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        data = s.validated_data

        connect = GradeService.create_sheet(
            subject=data["subject"],
            group=data["group"],
            students=data["students"]
        )

        return Response({
            "success": True,
            "connect_id": str(connect.id)
        }, status=status.HTTP_201_CREATED)


class CalculateJNView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="JN hisoblash",
        responses={
            200: openapi.Response(
                description="Hisoblandi",
                examples={
                    "application/json": {
                        "success": True,
                        "updated": 120
                    }
                }
            )
        },
        tags=["Vedmost"]
    )
    def post(self, request, connect_id):
        connect = ConnectGrades.objects.get(id=connect_id)

        count = GradeService.calculate_jn(connect)

        return Response({
            "success": True,
            "updated": count
        })

class ConnectGradeListView(ListAPIView):
    serializer_class = ConnectGradeListSerializer
    permission_classes = [IsAdmin]
    pagination_class = CustomPageNumberPagination   # 👈 qo‘shildi

    def get_queryset(self):
        queryset = (
            ConnectGrades.objects
            .select_related(
                "subject",
                "subject__subject",
                "subject__subject_curriculum",
                "subject__subject_semestr",
                "group"
            )
        )

        # 🔎 filtering
        params = self.request.query_params

        if subject := params.get("subject"):
            queryset = queryset.filter(subject_id=subject)

        if curriculum := params.get("curriculum"):
            queryset = queryset.filter(subject__subject_curriculum_id=curriculum)

        if semester := params.get("semester"):
            queryset = queryset.filter(subject__subject_semestr_id=semester)

        if group := params.get("group"):
            queryset = queryset.filter(group_id=group)

        return queryset.order_by("-id")  # pagination uchun stable ordering

    @swagger_auto_schema(
        operation_summary="Vedomostlar ro‘yxati",
        operation_description="O‘quv reja, semestr, fan va guruh bo‘yicha vedomostlar",
        manual_parameters=[
            openapi.Parameter("subject", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("curriculum", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("semester", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("group", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("page_size", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        responses={200: ConnectGradeListSerializer(many=True)},
        tags=["Vedmost"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class GradeDetailView(ListAPIView):
    serializer_class = GradeDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Grade.objects
            .filter(connect_grade_id=self.kwargs["connect_id"])
            .select_related("student")
        )

    @swagger_auto_schema(
        operation_summary="Vedomost ichini ko‘rish",
        operation_description="Talabalar va ularning JN/ON/YN ballari",
        responses={
            200: GradeDetailSerializer(many=True)
        },
        tags=["Vedmost"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CalculateONView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Oraliq nazorat (ON) hisoblash",
        operation_description="WrittenExam asosida ON ballarni hisoblaydi",
        tags=["Grade"]
    )
    def post(self, request, connect_id):
        connect = get_object_or_404(ConnectGrades, id=connect_id)

        count = calculate_on(connect)

        return Response({
            "success": True,
            "updated": count
        })

class CalculateYNView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Yakuniy nazorat (YN) hisoblash",
        tags=["Vedmost"]
    )
    def post(self, request, connect_id):
        connect = ConnectGrades.objects.get(id=connect_id)

        count = calculate_yn(connect)

        return Response({
            "success": True,
            "updated": count
        })

class StudentForGroupApiView(APIView):
    permission_classes = [IsAdmin,]
    serializer_class = StudentForGroupSerializer

    @swagger_auto_schema(
        operation_summary="Guruh bo‘yicha talabalar ro‘yxati",
        operation_description="Berilgan group_id bo‘yicha barcha talabalarni qaytaradi",
        manual_parameters=[
            openapi.Parameter(
                "group_id",
                openapi.IN_PATH,
                description="Guruh ID",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: StudentForGroupSerializer(many=True),
            404: openapi.Response(
                description="Talaba topilmadi",
                examples={
                    "application/json": {
                        "status": False,
                        "message": "Talaba topilmadi!"
                    }
                }
            ),
        },
        tags=["Vedmost"]
    )
    def get(self, request, group_id, *args, **kwargs):
        queryset = (
            Student.objects
            .filter(group_id=group_id)
            .select_related(
                "gender",
                "specialty",
                "studentStatus",
                "educationForm",
                "educationType",
                "educationYear",
                "paymentForm",
                "group",
                "faculty",
                "educationLang",
                "level",
                "semester",
                "country",
                "province",
                "district",
                "citizenship",
                "socialCategory",
                "accommodation",
            )
            .order_by("id")
        )

        if not queryset.exists():
            return Response(
                {
                    "status": False,
                    "message": "Talaba topilmadi!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)