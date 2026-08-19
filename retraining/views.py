from datetime import timedelta

from django import apps
from django.db.models import Q, Count, Prefetch
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status as status_codes
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
import io
import logging
from collections import defaultdict
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import utils
from django.db import models
from bigbluebutton.models import Bigbluebutton_Model
from shared.permissions import IsTeacher, IsStudent, IsTeacherOrStudent, IsAdminOrTeacher, IsAdminTeacherOrStudent
from students.models import Student
from user.permission import IsAdmin
from .models import ReTrainingGroup, ReTrainingStudent, Assignment, AssignmentSubmission, TestQuestion, TestAnswer, TestQuestionOption
from .serializers import ReTrainingGroup, ReTrainingStudent, \
    AssignmentSerializer, BulkStudentAddSerializer, ReTrainingStudentCreateSerializer, \
    AssignmentSubmissionSerializer, ReTrainingGroupBasicSerializer, ReTrainingGroupWithStudentsSerializer, \
    ReTrainingStudentBasicSerializer, ReTrainingStudentSerializer, StudentBasicSerializer, AssignmentCreateSerializer, \
    TestQuestionTeacherSerializer, TestQuestionStudentSerializer, AssignmentSerializerForStudent, \
    GradeSubmissionSerializer, SubmissionDetailSerializer, TextTestCreateSerializer, TestQuestionRetrieveSerializer
logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 101

MAX_UPLOAD_ATTEMPTS = 2  # Максимальное число попыток загрузки файла
MAX_FILE_SIZE_MB = 30    # Максимальный размер файла в МБ


class ReTrainingGroupListCreateAPIView(APIView):
    """
    Qayta o‘qitish guruhlari ro‘yxati yoki yangi guruh yaratish.
    """
    permission_classes = [IsAdminOrTeacher]
    pagination_class = StandardResultsSetPagination

    # --- Swagger parametrlari GET uchun ---
    search_param = openapi.Parameter(
        'search', openapi.IN_QUERY, description="Nom va tavsif bo‘yicha qidirish", type=openapi.TYPE_STRING
    )
    teacher_param = openapi.Parameter(
        'teacher', openapi.IN_QUERY, description="O‘qituvchi ID raqami", type=openapi.TYPE_STRING
    )
    language_param = openapi.Parameter(
        'language', openapi.IN_QUERY, description="O‘qitish tili ID raqami", type=openapi.TYPE_STRING
    )
    active_param = openapi.Parameter(
        'active_only', openapi.IN_QUERY, description="Faqat faol guruhlarni ko‘rsatish (true/false)", type=openapi.TYPE_BOOLEAN
    )
    sort_by_param = openapi.Parameter(
        'sort_by', openapi.IN_QUERY, description="Saralash maydoni (standart: -created_at)", type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(
        operation_summary="Qayta o‘qitish guruhlari ro‘yxati",
        operation_description="Barcha qayta o‘qitish guruhlarini filtrlash va saralash imkoniyati bilan olish.",
        manual_parameters=[search_param, teacher_param, language_param, active_param, sort_by_param],
        responses={200: ReTrainingGroupBasicSerializer(many=True)}
    )
    def get(self, request):
        groups = ReTrainingGroup.objects.select_related(
            'teacher', 'language',
        ).prefetch_related('retraining_students')

        if not request.user.is_superuser:
            groups = groups.filter(teacher=request.user)

        # Filtrlash
        search = request.query_params.get('search')
        teacher_id = request.query_params.get('teacher')
        language_id = request.query_params.get('language')
        active_only = request.query_params.get('active_only', 'false').lower() == 'true'

        if search:
            groups = groups.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if teacher_id:
            groups = groups.filter(teacher_id=teacher_id)
        if language_id:
            groups = groups.filter(language_id=language_id)
        if active_only:
            groups = groups.filter(is_active=True)

        sort_by = request.query_params.get('sort_by', '-created_at')
        groups = groups.order_by(sort_by)

        # Paginatsiya
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(groups, request)
        serializer = ReTrainingGroupBasicSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Qayta o‘qitish guruhi yaratish",
        operation_description="Yangi qayta o‘qitish guruhini yaratish. O‘qituvchi avtomatik belgilanadi.",
        request_body=ReTrainingGroupBasicSerializer,
        responses={
            201: ReTrainingGroupBasicSerializer,
            400: "Tekshiruv xatolari"
        }
    )
    def post(self, request):
        serializer = ReTrainingGroupBasicSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()  # teacher endi request.data dan olinadi
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReTrainingGroupDetailAPIView(APIView):
    """
    Qayta o‘qitish guruhi haqida ma’lumotni olish, yangilash yoki o‘chirish.
    """
    permission_classes = [IsAdminOrTeacher]

    def get_object(self, pk):
        return get_object_or_404(
            ReTrainingGroup.objects.select_related(
                'teacher', 'language', 'faculty', 'speciality'
            ).prefetch_related('retraining_students'),
            pk=pk
        )

    # So‘rov parametri: include_students
    include_students_param = openapi.Parameter(
        'include_students',
        openapi.IN_QUERY,
        description="Javobga talabalarni ham qo‘shish (true/false)",
        type=openapi.TYPE_BOOLEAN
    )

    @swagger_auto_schema(
        operation_summary="Guruh haqida ma’lumotni olish",
        operation_description="Qayta o‘qitish guruhi bo‘yicha batafsil ma’lumotni qaytaradi. "
                              "Agar include_students=true bo‘lsa, talabalarning ro‘yxati ham qaytariladi.",
        manual_parameters=[include_students_param],
        responses={200: ReTrainingGroupWithStudentsSerializer}
    )
    def get(self, request, pk):
        group = self.get_object(pk)

        if not request.user.is_superuser and group.teacher != request.user:
            return Response({'detail': 'Huquq yetarli emas.'}, status=status.HTTP_403_FORBIDDEN)

        include_students = request.query_params.get('include_students', 'false').lower() == 'true'
        serializer_class = ReTrainingGroupWithStudentsSerializer if include_students else ReTrainingGroupBasicSerializer
        serializer = serializer_class(group)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Guruh ma’lumotlarini to‘liq yangilash (PUT)",
        operation_description="Qayta o‘qitish guruhi ma’lumotlarini to‘liq yangilaydi.",
        request_body=ReTrainingGroupBasicSerializer,
        responses={
            200: ReTrainingGroupBasicSerializer,
            400: "Tekshiruv (validatsiya) xatosi",
            403: "Huquq yetarli emas"
        }
    )
    def put(self, request, pk):
        group = self.get_object(pk)
        if not request.user.is_superuser and group.teacher != request.user:
            return Response({'detail': 'Huquq yetarli emas.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReTrainingGroupBasicSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Guruh ma’lumotlarini qisman yangilash (PATCH)",
        operation_description="Qayta o‘qitish guruhi ma’lumotlarini qisman yangilaydi.",
        request_body=ReTrainingGroupBasicSerializer,
        responses={
            200: ReTrainingGroupBasicSerializer,
            400: "Tekshiruv (validatsiya) xatosi",
            403: "Huquq yetarli emas"
        }
    )
    def patch(self, request, pk):
        group = self.get_object(pk)
        if not request.user.is_superuser and group.teacher != request.user:
            return Response({'detail': 'Huquq yetarli emas.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReTrainingGroupBasicSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Guruhni o‘chirish",
        operation_description="Faol talabalari bo‘lmasa, qayta o‘qitish guruhini o‘chiradi.",
        responses={
            204: "Muvaffaqiyatli o‘chirildi",
            400: "Faol talabalar mavjud",
            403: "Huquq yetarli emas"
        }
    )
    def delete(self, request, pk):
        group = self.get_object(pk)
        if not request.user.is_superuser and group.teacher != request.user:
            return Response({'detail': 'Huquq yetarli emas.'}, status=status.HTTP_403_FORBIDDEN)

        if group.retraining_students.filter(is_active=True).exists():
            return Response({
                "detail": "Faol talabalari bor guruhni o‘chirib bo‘lmaydi. "
                          "Barcha talabalarni boshqa guruhlarga ko‘chiring yoki chetlashtiring."
            }, status=status.HTTP_400_BAD_REQUEST)

        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReTrainingStudentListAPIView(APIView):
    """
    Qayta o‘qitish guruhidagi talabalar ro‘yxati.
    """
    permission_classes = [IsAdminOrTeacher]

    # Swagger query-parametrlar
    status_param = openapi.Parameter(
        'status', openapi.IN_QUERY,
        description="Talaba holati bo‘yicha filtr (masalan: pending, accepted, rejected)",
        type=openapi.TYPE_STRING
    )
    active_only_param = openapi.Parameter(
        'active_only', openapi.IN_QUERY,
        description="Faqat faol talabalarni ko‘rsatish (standart qiymat — true)",
        type=openapi.TYPE_BOOLEAN
    )

    @swagger_auto_schema(
        operation_summary="Qayta o‘qitish guruhi talabalari ro‘yxati",
        operation_description="Ko‘rsatilgan qayta o‘qitish guruhiga biriktirilgan talabalar ro‘yxatini olish.",
        manual_parameters=[status_param, active_only_param],
        responses={200: ReTrainingStudentBasicSerializer(many=True)}
    )
    def get(self, request, group_pk):
        """Guruhdagi barcha talabalarni olish"""
        group = get_object_or_404(ReTrainingGroup, pk=group_pk)

        if not request.user.is_superuser and group.teacher != request.user:
            return Response({'detail': 'Huquq yetarli emas.'}, status=403)

        students_qs = ReTrainingStudent.objects.filter(group=group).select_related(
            'student', 'enrolled_by'
        )

        # Holat bo‘yicha filtr
        status_filter = request.query_params.get('status')
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'

        if status_filter:
            students_qs = students_qs.filter(status=status_filter)

        if active_only:
            students_qs = students_qs.filter(is_active=True)

        students_qs = students_qs.order_by('-enrolled_at')

        serializer = ReTrainingStudentBasicSerializer(students_qs, many=True)
        return Response(serializer.data)


class ReTrainingStudentAddAPIView(APIView):
    """
    Qayta o‘qitish guruhiga bitta talaba qo‘shish.
    """
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Qayta o‘qitish guruhiga bitta talaba qo‘shish",
        operation_description=(
            "Ko‘rsatilgan qayta o‘qitish guruhiga bitta talaba qo‘shadi, "
            "agar ro‘yxatdan o‘tish ochiq bo‘lsa va limit oshmagan bo‘lsa."
        ),
        request_body=ReTrainingStudentCreateSerializer,
        responses={
            201: ReTrainingStudentBasicSerializer,
            400: "Ma'lumotlarni tekshirishda xatolik",
            403: "Huquq yetarli emas"
        }
    )
    @transaction.atomic
    def post(self, request):
        serializer = ReTrainingStudentCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            retraining_student = serializer.save()
            response_serializer = ReTrainingStudentBasicSerializer(retraining_student)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReTrainingStudentAddToGroupAPIView(APIView):
    """
    Qayta o‘qitishning aniq guruhiga talaba qo‘shish.
    """
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Aniq guruhga talaba qo‘shish",
        operation_description=(
            "Ko‘rsatilgan qayta o‘qitish guruhiga bitta talaba qo‘shadi. "
            "`group_pk` qiymati URL orqali uzatiladi."
        ),
        request_body=ReTrainingStudentCreateSerializer,
        responses={
            201: ReTrainingStudentBasicSerializer,
            400: "Ma'lumotlarni tekshirishda xatolik",
            403: "Huquq yetarli emas"
        }
    )
    @transaction.atomic
    def post(self, request, group_pk):
        group = get_object_or_404(ReTrainingGroup, pk=group_pk)

        if not request.user.is_superuser and group.teacher != request.user:
            return Response(
                {"detail": "Bu guruhga talaba qo‘shish uchun huquqingiz yetarli emas."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        data['group'] = group.pk

        serializer = ReTrainingStudentCreateSerializer(
            data=data,
            context={'request': request}
        )

        if serializer.is_valid():
            student_obj = serializer.save()
            response_serializer = ReTrainingStudentBasicSerializer(student_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReTrainingStudentDetailAPIView(APIView):
    """
    Qayta o‘qitish talabasi haqidagi ma’lumotlarni olish, yangilash yoki o‘chirish.
    """
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        return get_object_or_404(
            ReTrainingStudent.objects.select_related('student', 'group', 'enrolled_by'),
            pk=pk
        )

    def has_permission_for_group(self, user, group):
        return (
            user.is_superuser
            or IsAdmin().has_permission(self.request, self)
            or (group.teacher and group.teacher == user)
        )

    @swagger_auto_schema(
        operation_summary="Qayta o‘qitish talabasi haqida ma’lumot olish",
        operation_description="Berilgan ID bo‘yicha qayta o‘qitish talabasi haqida to‘liq ma’lumotni qaytaradi.",
        responses={200: ReTrainingStudentSerializer}
    )
    def get(self, request, pk):
        student = self.get_object(pk)
        serializer = ReTrainingStudentSerializer(student)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Talaba ma’lumotlarini to‘liq yangilash",
        operation_description="Qayta o‘qitish talabasi ma’lumotlarini barcha maydonlari bilan yangilaydi.",
        request_body=ReTrainingStudentSerializer,
        responses={
            200: ReTrainingStudentSerializer,
            400: "Ma’lumotlarni tekshirishda xatolik",
            403: "Huquq yetarli emas"
        }
    )
    def put(self, request, pk):
        student = self.get_object(pk)
        if not self.has_permission_for_group(request.user, student.group):
            return Response({'detail': 'Huquq yetarli emas'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReTrainingStudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Talaba ma’lumotlarini qisman yangilash",
        operation_description="Qayta o‘qitish talabasi ma’lumotlarining faqat ayrim maydonlarini yangilash imkonini beradi.",
        request_body=ReTrainingStudentSerializer,
        responses={
            200: ReTrainingStudentSerializer,
            400: "Ma’lumotlarni tekshirishda xatolik",
            403: "Huquq yetarli emas"
        }
    )
    def patch(self, request, pk):
        student = self.get_object(pk)
        if not self.has_permission_for_group(request.user, student.group):
            return Response({'detail': 'Huquq yetarli emas'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReTrainingStudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Talabani guruhdan o‘chirish",
        operation_description="Huquqlar to‘g‘ri bo‘lsa, qayta o‘qitish guruhidan talabani o‘chiradi.",
        responses={
            204: "Talaba muvaffaqiyatli o‘chirildi",
            403: "Huquq yetarli emas",
            404: "Talaba topilmadi"
        }
    )
    def delete(self, request, pk):
        student = self.get_object(pk)
        if not self.has_permission_for_group(request.user, student.group):
            return Response({'detail': 'Huquq yetarli emas'}, status=status.HTTP_403_FORBIDDEN)

        full_name = student.student.full_name
        group_name = student.group.name
        student.delete()

        return Response({
            'detail': f'Talaba {full_name} {group_name} guruhidan o‘chirildi.'
        }, status=status.HTTP_204_NO_CONTENT)



class ReTrainingStudentRemoveFromGroupAPIView(APIView):
    """
    Muayyan talabani muayyan guruhdan o‘chirish.
    """
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="Talabani guruhdan o‘chirish",
        operation_description=(
            "Ko‘rsatilgan qayta o‘qitish guruhidan aniq talabani o‘chiradi. "
            "`group_pk` — guruh ID raqami, `student_pk` — shu guruhdagi talabaning ID raqami."
        ),
        responses={
            204: openapi.Response(description="Talaba muvaffaqiyatli guruhdan o‘chirildi"),
            403: "Huquq yetarli emas",
            404: "Guruh yoki talaba topilmadi"
        }
    )
    def delete(self, request, group_pk, student_pk):
        """Muayyan guruhdan talabani o‘chirish"""
        group = get_object_or_404(ReTrainingGroup, pk=group_pk)
        student = get_object_or_404(ReTrainingStudent, pk=student_pk, group=group)

        student_name = student.student.full_name
        student.delete()

        return Response(
            {"detail": f"Talaba {student_name} {group.name} guruhidan muvaffaqiyatli o‘chirildi."},
            status=status.HTTP_204_NO_CONTENT
        )



class BulkStudentAddAPIView(APIView):
    """
    Guruhga talabalarni ommaviy qo‘shish.
    """
    permission_classes = [IsTeacher | IsAdmin]

    @swagger_auto_schema(
        operation_summary="Talabalarni ommaviy qo‘shish",
        operation_description=(
            "Ko‘rsatilgan guruhga bir nechta talabalarni bir vaqtning o‘zida qo‘shadi. "
            "Talabaning fakulteti va mutaxassisligi guruh bilan mos bo‘lishi shart. "
            "Agar mos kelmasa, talaba o‘tkazib yuboriladi."
        ),
        request_body=BulkStudentAddSerializer,
        responses={
            201: openapi.Response(
                description="Muvaffaqiyatli qo‘shildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'skipped_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'created_students': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT)
                        ),
                        'skipped_students': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'reason': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        ),
                    }
                )
            ),
            400: "Maʼlumotlarda xato",
            403: "Huquq yetarli emas",
        }
    )
    @transaction.atomic
    def post(self, request):
        serializer = BulkStudentAddSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        group: ReTrainingGroup = serializer.validated_data['group']
        student_ids = serializer.validated_data['student_ids']
        notes = serializer.validated_data.get('notes', '')

        try:
            Student = apps.get_model('students', 'Student')
        except LookupError:
            return Response({"detail": "Student modeli topilmadi"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        today = timezone.now().date()
        if group.registration_start and today < group.registration_start:
            return Response({"detail": "Ro‘yxatga olish boshlanmagan."}, status=status.HTTP_400_BAD_REQUEST)
        if group.registration_end and today > group.registration_end:
            return Response({"detail": "Ro‘yxatga olish yakunlangan."}, status=status.HTTP_400_BAD_REQUEST)

        current_count = group.retraining_students.filter(is_active=True).count()
        if current_count >= group.max_students:
            return Response({"detail": "Guruh sig‘imi limitidan oshib ketgan."}, status=status.HTTP_400_BAD_REQUEST)

        has_faculty_field = True
        try:
            Student._meta.get_field('faculty')
        except Exception:
            has_faculty_field = False

        students = Student.objects.filter(id__in=student_ids).select_related('specialty')
        if has_faculty_field:
            students = students.select_related('faculty')

        existing_ids = set(
            ReTrainingStudent.objects.filter(
                group=group, student__in=students, is_active=True
            ).values_list('student_id', flat=True)
        )

        created_students = []
        skipped_students = []
        students_by_id = {s.id: s for s in students}

        for sid in student_ids:
            student = students_by_id.get(sid)
            if not student:
                skipped_students.append({
                    'id': sid,
                    'name': f'#{sid}',
                    'reason': 'Talaba topilmadi'
                })
                continue

            if sid in existing_ids:
                skipped_students.append({
                    'id': student.id,
                    'name': getattr(student, 'full_name', f'#{student.id}'),
                    'reason': 'Talaba guruhda allaqachon mavjud'
                })
                continue


            if current_count + len(created_students) >= group.max_students:
                skipped_students.append({
                    'id': student.id,
                    'name': getattr(student, 'full_name', f'#{student.id}'),
                    'reason': 'Guruhdagi talabalar soni limitiga yetgan'
                })
                continue

            retraining_student = ReTrainingStudent.objects.create(
                student=student,
                group=group,
                notes=notes,
                enrolled_by=request.user
            )
            created_students.append(retraining_student)

        return Response({
            'success': True,
            'created_count': len(created_students),
            'skipped_count': len(skipped_students),
            'created_students': ReTrainingStudentBasicSerializer(created_students, many=True).data,
            'skipped_students': skipped_students
        }, status=status.HTTP_201_CREATED)



class ReTrainingStudentStatusUpdateAPIView(APIView):
    """
    Qayta o‘qitish talabasining statusini yangilash.
    """
    permission_classes = [IsAdminOrTeacher]

    @swagger_auto_schema(
        operation_summary="Qayta o‘qitish talabasining statusini yangilash",
        operation_description="Talabaning statusi va izohini yangilash imkonini beradi. "
                              "Agar status = `completed` bo‘lsa, tugallanish sanasi avtomatik saqlanadi.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["status"],
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Talabaning yangi statusi",
                    enum=[choice[0] for choice in ReTrainingStudent.STATUS_CHOICES]
                ),
                "notes": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Qo‘shimcha ma’lumot (izohlar)",
                ),
            }
        ),
        responses={
            200: ReTrainingStudentSerializer,
            400: "Ma’lumotlarni tekshirish xatosi",
            404: "Talaba topilmadi"
        }
    )
    @transaction.atomic
    def patch(self, request, pk):
        """Talaba statusini yangilash"""
        student = get_object_or_404(ReTrainingStudent, pk=pk)
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {"detail": "Status kiritilishi shart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_statuses = [choice[0] for choice in ReTrainingStudent.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Yaroqsiz status. Mavjudlari: {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = student.status
        student.status = new_status

        if new_status == 'completed' and not student.completion_date:
            student.completion_date = timezone.now()

        for field in ['notes']:
            if field in request.data:
                setattr(student, field, request.data[field])

        student.save()

        serializer = ReTrainingStudentSerializer(student)
        response_data = serializer.data
        response_data['status_changed'] = {
            'from': old_status,
            'to': new_status
        }

        return Response(response_data)


class ReTrainingStatisticsAPIView(APIView):
    """
    Qayta o‘qitish bo‘yicha statistika.
    """
    permission_classes = [IsAdminOrTeacher]

    @swagger_auto_schema(
        operation_summary="Qayta o‘qitish statistikasi",
        operation_description="Qayta o‘qitish bo‘yicha guruhlar, talabalar, o‘qituvchilar va tillar statistikasi qaytariladi.",
        responses={
            200: openapi.Response(
                description="Statistika bilan muvaffaqiyatli javob",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'groups': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total': openapi.Schema(type=openapi.TYPE_INTEGER, description="Jami guruhlar soni"),
                                'active': openapi.Schema(type=openapi.TYPE_INTEGER, description="Faol guruhlar soni"),
                                'by_status': openapi.Schema(type=openapi.TYPE_OBJECT, description="Status bo‘yicha guruhlar soni")
                            }
                        ),
                        'students': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total': openapi.Schema(type=openapi.TYPE_INTEGER, description="Jami talabalar soni"),
                                'active': openapi.Schema(type=openapi.TYPE_INTEGER, description="Faol talabalar soni"),
                                'by_status': openapi.Schema(type=openapi.TYPE_OBJECT, description="Status bo‘yicha talabalar soni")
                            }
                        ),
                        'top_teachers': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="O‘qituvchi ID raqami"),
                                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description="O‘qituvchi to‘liq ismi"),
                                'groups_count': openapi.Schema(type=openapi.TYPE_INTEGER, description="O‘qituvchi guruhlari soni"),
                            })
                        ),
                        'popular_languages': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Til ID raqami"),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description="Til nomi"),
                                'groups_count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Ushbu tilda guruhlar soni"),
                            })
                        ),
                        'generated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description="Statistika yaratilgan vaqt"),
                    }
                )
            )
        }
    )
    def get(self, request):
        """Qayta o‘qitish bo‘yicha umumiy statistika olish"""

        total_groups = ReTrainingGroup.objects.count()
        active_groups = ReTrainingGroup.objects.filter(is_active=True).count()
        group_status_counts = {
            status: {
                "count": ReTrainingGroup.objects.filter(status=status).count(),
                "label": label
            }
            for status, label in ReTrainingGroup.STATUS_CHOICES
        }

        total_students = ReTrainingStudent.objects.count()
        active_students = ReTrainingStudent.objects.filter(is_active=True).count()
        student_status_counts = {
            status: {
                "count": ReTrainingStudent.objects.filter(status=status).count(),
                "label": label
            }
            for status, label in ReTrainingStudent.STATUS_CHOICES
        }

        top_teachers = (
            ReTrainingGroup.objects
            .filter(teacher__isnull=False)
            .values('teacher_id', 'teacher__first_name', 'teacher__last_name')
            .annotate(groups_count=Count('id'))
            .order_by('-groups_count')[:5]
        )

        popular_languages = (
            ReTrainingGroup.objects
            .filter(language__isnull=False)
            .values('language_id', 'language__name')
            .annotate(groups_count=Count('id'))
            .order_by('-groups_count')[:5]
        )

        return Response({
            'groups': {
                'total': total_groups,
                'active': active_groups,
                'by_status': group_status_counts
            },
            'students': {
                'total': total_students,
                'active': active_students,
                'by_status': student_status_counts
            },
            'top_teachers': [
                {
                    'id': teacher['teacher_id'],
                    'full_name': f"{teacher['teacher__first_name']} {teacher['teacher__last_name']}".strip(),
                    'groups_count': teacher['groups_count']
                } for teacher in top_teachers
            ],
            'popular_languages': [
                {
                    'id': lang['language_id'],
                    'name': lang['language__name'],
                    'groups_count': lang['groups_count']
                } for lang in popular_languages
            ],
            'generated_at': timezone.now()
        })


# class AvailableStudentsAPIView(APIView):
#     """
#     Список доступных студентов для добавления в группу переобучения.
#     """
#     permission_classes = [IsTeacher]
#
#     # Swagger query-параметры
#     search_param = openapi.Parameter(
#         'search', openapi.IN_QUERY,
#         description="Поиск по ФИО, номеру студента или email",
#         type=openapi.TYPE_STRING
#     )
#     specialty_param = openapi.Parameter(
#         'specialty', openapi.IN_QUERY,
#         description="Фильтрация по ID специальности",
#         type=openapi.TYPE_INTEGER
#     )
#     group_param = openapi.Parameter(
#         'group', openapi.IN_QUERY,
#         description="Фильтрация по ID академической группы",
#         type=openapi.TYPE_INTEGER
#     )
#
#     @swagger_auto_schema(
#         operation_summary="Получить доступных студентов для переобучения",
#         operation_description="Возвращает список студентов, которые ещё не зарегистрированы в активных группах переобучения.",
#         manual_parameters=[search_param, specialty_param, group_param],
#         responses={200: StudentBasicSerializer(many=True)}
#     )
#     def get(self, request):
#         """Получить список студентов, доступных для переобучения"""
#         try:
#             Student = apps.get_model('students', 'Student')
#         except LookupError:
#             return Response(
#                 {"detail": "Модель Student не найдена"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#
#         enrolled_ids = ReTrainingStudent.objects.filter(
#             is_active=True,
#             status__in=['registered', 'studying']
#         ).values_list('student_id', flat=True)
#
#         students_qs = Student.objects.exclude(id__in=enrolled_ids).select_related('specialty', 'group')
#
#         search = request.query_params.get('search')
#         specialty_id = request.query_params.get('specialty')
#         group_id = request.query_params.get('group')
#
#         if search:
#             students_qs = students_qs.filter(
#                 Q(full_name__icontains=search) |
#                 Q(student_id_number__icontains=search) |
#                 Q(email__icontains=search)
#             )
#
#         if specialty_id:
#             students_qs = students_qs.filter(specialty_id=specialty_id)
#
#         if group_id:
#             students_qs = students_qs.filter(group_id=group_id)
#
#         paginator = StandardResultsSetPagination()
#         page = paginator.paginate_queryset(students_qs, request)
#
#         serializer = StudentBasicSerializer(page or students_qs, many=True)
#         if page is not None:
#             return paginator.get_paginated_response(serializer.data)
#
#         return Response(serializer.data)


class AssignmentListCreateAPIView(APIView):
    """
    Topshiriqlar ro‘yxatini olish va yangi topshiriq yaratish API.
    """
    permission_classes = [IsAdminOrTeacher]

    # --- Swagger filter parametrlari ---
    group_param = openapi.Parameter(
        'group', openapi.IN_QUERY,
        description="Topshiriq tegishli bo‘lgan guruh ID raqami",
        type=openapi.TYPE_STRING
    )
    type_param = openapi.Parameter(
        'type', openapi.IN_QUERY,
        description="Topshiriq turi (masalan: test, loyiha va h.k.)",
        type=openapi.TYPE_STRING
    )
    status_param = openapi.Parameter(
        'status', openapi.IN_QUERY,
        description="Topshiriq holati (masalan: active, draft va h.k.)",
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(
        operation_summary="Topshiriqlar ro‘yxati",
        operation_description="Topshiriqlar ro‘yxatini olish, guruh, turi va holati bo‘yicha filtrlash imkoniyati bilan.",
        manual_parameters=[group_param, type_param, status_param],
        responses={200: AssignmentSerializer(many=True)}
    )
    def get(self, request):
        queryset = Assignment.objects.select_related('group', 'created_by')

        group_id = request.query_params.get('group')
        assignment_type = request.query_params.get('type')
        assignment_status = request.query_params.get('status')

        if group_id:
            queryset = queryset.filter(group_id=group_id)
        if assignment_type:
            queryset = queryset.filter(assignment_type=assignment_type)
        if assignment_status:
            queryset = queryset.filter(status=assignment_status)

        serializer = AssignmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Yangi topshiriq yaratish",
        operation_description="Berilgan ma’lumotlarga asoslanib yangi topshiriq yaratadi.",
        request_body=AssignmentCreateSerializer,
        responses={
            201: openapi.Response(
                description="Topshiriq muvaffaqiyatli yaratildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Amal bajarilganligi"),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Natija xabari"),
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description="Yaratilgan topshiriq ID raqami"),
                    }
                )
            ),
            400: openapi.Response(
                description="Topshiriq yaratishda xatolik",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Amal bajarilganligi"),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Xatolik xabari"),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT, description="Xatolik tafsilotlari")
                    }
                )
            )
        }
    )
    def post(self, request):
        serializer = AssignmentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            assignment = serializer.save(created_by=request.user)
            return Response({
                'status': True,
                'message': 'Topshiriq muvaffaqiyatli yaratildi',
                'id': assignment.id
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': False,
            'errors': serializer.errors,
            'message': 'Topshiriq yaratishda xatolik'
        }, status=status.HTTP_400_BAD_REQUEST)


class TestTakeAPIView(APIView):
    """Начало прохождения теста"""

    @swagger_auto_schema(
        operation_summary="Testni boshlash",
        operation_description=(
                "Talaba uchun topshirishga urinish yaratadi va test savollarini qaytaradi"
                " (to‘g‘ri javob yo‘q). Standart holatda talaba avtorizatsiya qilingan foydalanuvchidan olinadi. "
                "Agar student_id uzatilsa - u talabaning PK raqami yoki student_id_number raqami bo‘lishi mumkin."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["assignment_id"],
            properties={
                "assignment_id": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
                "ip_address": openapi.Schema(type=openapi.TYPE_STRING),
                "student_id": openapi.Schema(type=openapi.TYPE_STRING, description="PK yoki o‘quv raqami"),
            },
        ),
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "submission_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "attempt_number": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "questions": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    }
                )
            ),
            400: "Tasdiqlashda xatolik yuz berdi / vaqt tugadi / urinishlar tugadi",
            403: "Testga kirish ruxsati yo‘q",
            404: "Hech qanday test topilmadi",
        }
    )
    @transaction.atomic
    def post(self, request):
        assignment_id = request.data.get('assignment_id')
        ip_address = request.data.get('ip_address') or request.META.get('REMOTE_ADDR')
        student_id_raw = request.data.get('student_id')

        # 1) Задание
        try:
            assignment = Assignment.objects.get(id=assignment_id, assignment_type='test')
        except Assignment.DoesNotExist:
            return Response({"status": False, "message": "Hech qanday test topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        # 2) Проверка статуса/времени
        now = timezone.now()
        if assignment.status != 'active':
            return Response({"status": False, "message": "Test faol emas"}, status=status.HTTP_400_BAD_REQUEST)
        if assignment.start_datetime and now < assignment.start_datetime:
            return Response({"status": False, "message": "Test hali boshlanmadi"}, status=status.HTTP_400_BAD_REQUEST)
        if assignment.end_datetime and now > assignment.end_datetime:
            return Response({"status": False, "message": "Test vaqti tugadi"}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Определяем retraining_student
        retraining_student = None

        # 3a) Если передан student_id — пробуем найти студента и его участие в группе
        if student_id_raw:
            student_obj = None
            # пробуем как PK
            if str(student_id_raw).isdigit():
                student_obj = Student.objects.filter(id=int(student_id_raw)).first()
            # если не нашли — пробуем как student_id_number
            if not student_obj:
                student_obj = Student.objects.filter(student_id_number=str(student_id_raw)).first()

            if not student_obj:
                return Response({"status": False, "message": "Talaba topilmadi student_id"},
                                status=status.HTTP_404_NOT_FOUND)

            retraining_student = ReTrainingStudent.objects.filter(
                student=student_obj, group=assignment.group, is_active=True
            ).first()
        else:
            # 3b) По авторизованному пользователю
            retraining_student = ReTrainingStudent.objects.filter(
                student__user=request.user, group=assignment.group, is_active=True
            ).first()

        if not retraining_student:
            return Response({"status": False, "message": "Talaba bu testdan foydalana olmaydi"},
                            status=status.HTTP_403_FORBIDDEN)

        # 4) Проверка количества попыток
        attempts_count = AssignmentSubmission.objects.filter(
            assignment=assignment, student=retraining_student
        ).count()

        if attempts_count >= assignment.max_attempts:
            return Response({
                "status": False,
                "message": f"Maksimal urinishlar soni oshib ketdi ({assignment.max_attempts})"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 5) Создаём попытку
        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=retraining_student,
            attempt_number=attempts_count + 1,
            defaults={"ip_address": ip_address, "status": "in_progress"}
        )

        # 6) Вопросы для студента
        questions_qs = TestQuestion.objects.filter(
            assignment=assignment, is_active=True
        ).prefetch_related('options')

        if assignment.randomize_questions:
            # учитываем лимит вопроса, если задан
            limit = assignment.question_count or questions_qs.count()
            questions_qs = questions_qs.order_by('?')[:limit]
        else:
            questions_qs = questions_qs.order_by('order', 'id')

        # сохраняем snapshot вопросов в попытке (без правильных ответов)
        snapshot = []
        for q in questions_qs:
            snapshot.append({
                "id": str(q.id),  # 👈 UUID -> str
                "question_text": q.question_text,
                "question_type": q.question_type,
                "points": q.points,
            })

        submission.test_data = snapshot
        submission.save(update_fields=['test_data'])

        # сериализация для студента — без correct_answer и без options.is_correct
        questions_data = TestQuestionStudentSerializer(questions_qs, many=True).data

        return Response({
            "status": True,
            "submission_id": submission.id,
            "attempt_number": submission.attempt_number,
            "questions": questions_data
        }, status=status.HTTP_200_OK)


class TestSubmitAPIView(APIView):
    """
    Test javoblarini yuborish API (takomillashtirilgan)
    - qayta topshirishga ruxsat yo'q
    - vaqt cheklovlari tekshiriladi
    """

    @swagger_auto_schema(
        operation_summary="Test javoblarini topshirish",
        operation_description="Talaba test javoblarini yuboradi. "
                              "Qayta topshirishga ruxsat berilmaydi. "
                              "Umumiy va individual vaqt cheklovlari tekshiriladi. "
                              "Agar topshiriq sozlamalarida ko'rsatilgan bo'lsa, natija darhol hisoblanadi.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["submission_id", "answers"],
            properties={
                "submission_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Topshirish ID raqami"
                ),
                "answers": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Test javoblari massivi",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "question_id": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Savol ID raqami"
                            ),
                            "selected_options": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description="Tanlangan variantlar ID lari (single_choice/multiple_choice uchun)",
                                items=openapi.Schema(type=openapi.TYPE_INTEGER)
                            ),
                            "text_answer": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Matnli javob (text/number savollar uchun)"
                            )
                        },
                        required=["question_id"]
                    )
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Test muvaffaqiyatli topshirildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="Amaliyot natijasi"
                        ),
                        "submission_id": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Topshirish ID raqami"
                        ),
                        "score": openapi.Schema(
                            type=openapi.TYPE_NUMBER,
                            description="Olingan ball"
                        ),
                        "max_score": openapi.Schema(
                            type=openapi.TYPE_NUMBER,
                            description="Maksimal ball"
                        ),
                        "grade": openapi.Schema(
                            type=openapi.TYPE_NUMBER,
                            description="Foiz (%)"
                        ),
                        "percentage": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Foizli ko'rinishda"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Xatolik yuz berdi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
                examples={
                    "application/json": {
                        "status": False,
                        "message": "Bu test allaqachon yakunlangan. Qayta yuborish taqiqlangan."
                    }
                }
            ),
            404: openapi.Response(
                description="Topshirish topilmadi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Xabar"
                        )
                    }
                )
            )
        }
    )
    @transaction.atomic
    def post(self, request):
        submission_id = request.data.get('submission_id')
        answers = request.data.get('answers', [])

        if not submission_id or not answers:
            return Response({
                'status': False,
                'message': 'submission_id va answers kiritilishi shart'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 1) Urinishni topamiz
        submission = get_object_or_404(
            AssignmentSubmission,
            id=submission_id
        )

        assignment = submission.assignment
        now = timezone.now()

        # 2) ❗ QAYTA TOPSHIRISHGA YO‘L YO‘Q
        if submission.status in ['completed', 'graded', 'overdue']:
            return Response({
                'status': False,
                'message': 'Bu test allaqachon yakunlangan. Qayta yuborish taqiqlangan.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if submission.status != 'in_progress':
            return Response({
                'status': False,
                'message': 'Urinish yaroqsiz holatda'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3) ❗ UMUMIY TEST VAQTI TUGAGANMI?
        if now > assignment.end_datetime:
            submission.status = 'overdue'
            submission.completed_at = now
            submission.save()
            return Response({
                'status': False,
                'message': 'Test vaqti tugagan'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4) ❗ INDIVIDUAL TAYMER (duration_minutes)
        if assignment.duration_minutes:
            deadline = submission.started_at + timedelta(minutes=assignment.duration_minutes)
            if now > deadline:
                submission.status = 'overdue'
                submission.completed_at = now
                submission.save()
                return Response({
                    'status': False,
                    'message': f"Test uchun ajratilgan vaqt tugadi ({assignment.duration_minutes} daqiqa)."
                }, status=status.HTTP_400_BAD_REQUEST)

        # 5) Javoblarni tekshirish
        total_score = 0
        max_possible_score = 0

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            if not question_id:
                continue

            try:
                question = TestQuestion.objects.get(id=question_id, assignment=assignment)
            except TestQuestion.DoesNotExist:
                continue

            test_answer = TestAnswer.objects.create(
                submission=submission,
                question=question
            )

            if question.question_type in ['single_choice', 'multiple_choice']:
                selected_ids = answer_data.get('selected_options', [])
                options = TestQuestionOption.objects.filter(id__in=selected_ids, question=question)
                test_answer.selected_options.set(options)

            elif question.question_type in ['text', 'number']:
                test_answer.text_answer = answer_data.get('text_answer', '')

            test_answer.check_answer()

            total_score += test_answer.points_earned or 0
            max_possible_score += question.points or 0

        # 6) Yakuniy natija
        submission.score = total_score
        submission.max_score = max_possible_score
        submission.grade = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        submission.completed_at = now

        # Natijani ko‘rsatish
        if assignment.show_results_immediately:
            submission.status = 'graded'
            submission.graded_at = now
        else:
            submission.status = 'completed'

        submission.save()

        return Response({
            'status': True,
            'submission_id': submission.id,
            'score': total_score,
            'max_score': max_possible_score,
            'grade': round(submission.grade, 2),
            'percentage': submission.percentage_score
        }, status=status.HTTP_200_OK)


class TestQuestionsAPIView(APIView):
    """
    Test savollarini olish API.
    """
    permission_classes = [IsAdminTeacherOrStudent]

    def get_assignment(self, assignment_id):
        """Получение задания с оптимизацией запроса"""
        try:
            return Assignment.objects.select_related('group', 'created_by').get(
                id=assignment_id,
                assignment_type='test'
            )
        except Assignment.DoesNotExist:
            raise Http404("Test topilmadi")

    def check_student_access(self, user, group):
        """Проверка доступа студента к группе"""
        # Проверяем является ли пользователь staff или superuser (учитель/админ)
        if user.is_staff or user.is_superuser:
            return True

        # Для обычных пользователей проверяем доступ к группе
        return ReTrainingStudent.objects.filter(
            student__user=user,
            group=group,
            is_active=True
        ).exists()

    def check_teacher_access(self, assignment, user):
        """Проверка доступа учителя"""
        return assignment.created_by == user or user.is_staff or user.is_superuser

    def get(self, request, assignment_id):
        try:
            # 1. Получаем задание
            assignment = self.get_assignment(assignment_id)

            # 2. Проверяем доступ
            is_teacher = self.check_teacher_access(assignment, request.user)
            is_student = self.check_student_access(request.user, assignment.group)

            user_type = "teacher" if is_teacher else "student" if is_student else "unknown"

            if not (is_teacher or is_student):
                return Response({
                    'status': False,
                    'message': 'Sizda ushbu testga kirish huquqi yo\'q'
                }, status=status.HTTP_403_FORBIDDEN)

            # 3. Дополнительная проверка для студентов
            if is_student:
                if assignment.status != 'active':
                    return Response({
                        'status': False,
                        'message': 'Test hali boshlanmagan yoki tugagan'
                    }, status=status.HTTP_403_FORBIDDEN)

                now = timezone.now()
                if assignment.start_datetime and now < assignment.start_datetime:
                    return Response({
                        'status': False,
                        'message': 'Test hali boshlanmadi'
                    }, status=status.HTTP_403_FORBIDDEN)

                if assignment.end_datetime and now > assignment.end_datetime:
                    return Response({
                        'status': False,
                        'message': 'Test vaqti tugagan'
                    }, status=status.HTTP_403_FORBIDDEN)

            # 4. Получаем вопросы (ИСПРАВЛЕННАЯ ЧАСТЬ)
            questions = TestQuestion.objects.filter(
                assignment=assignment,
                is_active=True  # Это поле ЕСТЬ в TestQuestion
            ).prefetch_related(
                Prefetch('options', queryset=TestQuestionOption.objects.all())  # Все опции
            ).order_by('order')

            if not questions.exists():
                return Response({
                    'status': False,
                    'message': 'Testda hali savollar mavjud emas'
                }, status=status.HTTP_404_NOT_FOUND)

            # 5. Выбираем сериализатор
            if is_teacher:
                serializer = TestQuestionTeacherSerializer(questions, many=True)
            else:
                serializer = TestQuestionStudentSerializer(questions, many=True)

            # 6. Рассчитываем баллы
            max_points = sum(question.points for question in questions)

            # 7. Возвращаем ответ
            response_data = {
                'status': True,
                'assignment_id': str(assignment.id),
                'assignment_title': assignment.title,
                'assignment_status': assignment.status,
                'total_questions': questions.count(),
                'max_points': max_points,
                'user_type': user_type,
                'questions': serializer.data
            }

            # 8. Информация о времени для студентов
            if is_student:
                if assignment.duration_minutes:
                    response_data['time_limit_minutes'] = assignment.duration_minutes

                if assignment.end_datetime:
                    remaining_time = assignment.end_datetime - timezone.now()
                    response_data['remaining_seconds'] = max(0, int(remaining_time.total_seconds()))

            return Response(response_data, status=status.HTTP_200_OK)

        except Http404:
            return Response({
                'status': False,
                'message': 'Test topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"TestQuestionsAPIView error for assignment {assignment_id}: {str(e)}", exc_info=True)
            return Response({
                'status': False,
                'message': 'Server xatosi yuz berdi'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssignmentSubmitAPIView(APIView):
    """
    Fayl bilan topshiriqni topshirish API.
    """
    permission_classes = [IsAdminTeacherOrStudent]

    @swagger_auto_schema(
        operation_summary="Fayl bilan topshiriq topshirish",
        operation_description="Talabaga topshiriqni fayl orqali topshirishga imkon beradi. "
                              "Vaqt, status, urinishlar soni va guruhga tegishliligi tekshiriladi.",
        manual_parameters=[
            openapi.Parameter(
                name="pk",
                in_=openapi.IN_PATH,
                description="Topshiriq ID raqami",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["submission_file"],
            properties={
                "submission_file": openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description="Topshiriq fayli"
                ),
                "student_comment": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Talaba izohi (majburiy emas)"
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Topshiriq muvaffaqiyatli topshirildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: "Xatolik: fayl yo‘q, topshiriq mavjud emas, urinishlar soni limitdan oshgan va hokazo",
            403: "Kirish taqiqlangan: siz guruh talabasi emassiz",
            404: "Topshiriq topilmadi"
        }
    )
    @transaction.atomic
    def post(self, request, pk):
        """Fayl bilan topshiriqni topshirish"""
        assignment = get_object_or_404(Assignment, id=pk, assignment_type='assignment')

        try:
            retraining_student = ReTrainingStudent.objects.get(
                student__user=request.user,
                group=assignment.group,
                is_active=True
            )
        except ReTrainingStudent.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Siz ushbu guruh talabasi emassiz'
            }, status=status.HTTP_403_FORBIDDEN)

        now = timezone.now()
        if not (assignment.start_datetime <= now <= assignment.end_datetime):
            return Response({
                'status': False,
                'message': 'Topshiriq vaqti tugagan yoki hali boshlanmagan'
            }, status=status.HTTP_400_BAD_REQUEST)

        if assignment.status != 'active':
            return Response({
                'status': False,
                'message': 'Topshiriq faol emas'
            }, status=status.HTTP_400_BAD_REQUEST)

        attempts_count = AssignmentSubmission.objects.filter(
            assignment=assignment,
            student=retraining_student
        ).count()

        if attempts_count >= assignment.max_attempts:
            return Response({
                'status': False,
                'message': f'Urinishlar soni ({assignment.max_attempts}) limitdan oshgan'
            }, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get('submission_file')
        if not file:
            return Response({
                'status': False,
                'message': 'Topshiriq faylini yuklash majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)

        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=retraining_student,
            attempt_number=attempts_count + 1,
            submission_file=file,
            student_comment=request.data.get('student_comment', ''),
            status='completed',
            completed_at=now,
            ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )

        serializer = AssignmentSubmissionSerializer(submission)
        return Response({
            'status': True,
            'message': 'Topshiriq muvaffaqiyatli topshirildi',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class TeacherUploadAssignmentFileAPIView(APIView):
    """
    Учитель загружает (POST) или просматривает (GET) файл в Assignment.
    Можно загрузить только один файл на задание.
    """
    permission_classes = [IsAdminTeacherOrStudent]

    # --- GET METHOD ---
    @swagger_auto_schema(
        operation_summary="Yuklangan faylni ko'rish",
        operation_description="Topshiriqqa biriktirilgan fayl haqida ma'lumot olish.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "file_url": openapi.Schema(type=openapi.TYPE_STRING),
                    "file_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "upload_count": openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            404: "Fayl topilmadi"
        }
    )
    def get(self, request, id):
        assignment = get_object_or_404(Assignment, id=id)

        if not assignment.assignment_file:
            return Response({
                "status": False,
                "message": "Fayl hali yuklanmagan"
            }, status=status.HTTP_404_NOT_FOUND)

        file_url = request.build_absolute_uri(assignment.assignment_file.url)

        return Response({
            "status": True,
            "file_url": file_url,
            "file_name": assignment.assignment_file.name.split('/')[-1],
            "upload_count": getattr(assignment, 'upload_count', 1)
        }, status=status.HTTP_200_OK)

    # --- POST METHOD ---
    @swagger_auto_schema(
        operation_summary="O'qituvchi topshiriqqa fayl yuklaydi",
        operation_description=f"Faol bo'lmagan topshiriqqa faqat BITTA fayl biriktirish mumkin. Maksimal hajm: {MAX_FILE_SIZE_MB}MB.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["file"],
            properties={
                "file": openapi.Schema(type=openapi.TYPE_FILE)
            }
        ),
        responses={
            200: "Fayl biriktirildi",
            400: "Xatolik (fayl mavjud yoki limit)",
            403: "Ruxsat yo'q"
        }
    )
    def post(self, request, id):
        assignment = get_object_or_404(Assignment, id=id)

        # 1️⃣ Проверка типа задания
        if assignment.assignment_type != "assignment":
            return Response({
                "status": False,
                "message": "Bu faylli topshiriq emas (assignment_type='assignment' bo'lishi kerak)"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2️⃣ Проверка статуса (если ACTIVE — нельзя)
        if assignment.status == "active":
            return Response({
                "status": False,
                "message": "Faol bo'lgan topshiriqqa fayl yuklab bo'lmaydi"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ ОГРАНИЧЕНИЕ: Проверка, что файл уже загружен
        if assignment.assignment_file:
            return Response({
                "status": False,
                "message": "Bu topshiriqqa allaqachon fayl biriktirilgan. Yangi fayl yuklash uchun avval mavjud faylni o'chiring."
            }, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get("file")
        if not file:
            return Response({
                "status": False,
                "message": "Fayl yuklash majburiy"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4️⃣ ОГРАНИЧЕНИЕ ПО РАЗМЕРУ ФАЙЛА (Size Limit)
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return Response({
                "status": False,
                "message": f"Fayl hajmi juda katta. Maksimal: {MAX_FILE_SIZE_MB}MB"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 5️⃣ Сохранение файла
        assignment.assignment_file = file
        assignment.status = "published"

        # Обновляем счетчик загрузок (если поле существует)
        if hasattr(assignment, 'upload_count'):
            assignment.upload_count = 1  # Всегда 1, так как только один файл разрешен
            assignment.save(update_fields=["assignment_file", "status", "upload_count"])
        else:
            assignment.save(update_fields=["assignment_file", "status"])

        return Response({
            "status": True,
            "message": "Topshiriqqa fayl muvaffaqiyatli yuklandi",
            "assignment_id": assignment.id,
            "file_name": assignment.assignment_file.name,
            "upload_count": 1,  # Всегда 1 файл
            "status_updated_to": assignment.status
        }, status=status.HTTP_200_OK)

    # --- DELETE METHOD ---
    @swagger_auto_schema(
        operation_summary="Topshiriqdan faylni o'chirish",
        operation_description="Topshiriqdan biriktirilgan faylni o'chiradi, yangi fayl yuklash imkoniyati ochiladi.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: "Fayl muvaffaqiyatli o'chirildi",
            404: "Fayl topilmadi"
        }
    )
    def delete(self, request, id):
        assignment = get_object_or_404(Assignment, id=id)

        if not assignment.assignment_file:
            return Response({
                "status": False,
                "message": "O'chirish uchun fayl mavjud emas"
            }, status=status.HTTP_404_NOT_FOUND)

        # Сохраняем информацию о файле перед удалением
        file_name = assignment.assignment_file.name

        # Удаляем файл из storage
        assignment.assignment_file.delete(save=False)

        # Очищаем поле файла в модели
        assignment.assignment_file = None
        assignment.status = "draft"  # Или другой подходящий статус

        # Сбрасываем счетчик загрузок (если поле существует)
        if hasattr(assignment, 'upload_count'):
            assignment.upload_count = 0
            assignment.save(update_fields=["assignment_file", "status", "upload_count"])
        else:
            assignment.save(update_fields=["assignment_file", "status"])

        return Response({
            "status": True,
            "message": "Fayl muvaffaqiyatli o'chirildi",
            "deleted_file": file_name,
            "assignment_id": assignment.id,
            "current_status": assignment.status
        }, status=status.HTTP_200_OK)


class AssignmentResultsAPIView(APIView):
    """
    Topshiriq natijalarini olish API.
    """
    permission_classes = [IsAdminTeacherOrStudent]

    @swagger_auto_schema(
        operation_summary="Topshiriq natijalarini olish",
        operation_description="Topshiriq bo‘yicha topshirilgan ishlar ro‘yxatini qaytaradi, statistika bilan birga. "
                              "Status bo‘yicha, talaba bo‘yicha filtrlash va faqat so‘nggi urinishlarni olish imkoniyati mavjud.",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                description='Topshiriq ID raqami',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='status',
                in_=openapi.IN_QUERY,
                description='Topshirish statusi bo‘yicha filtrlash (`in_progress`, `completed`, `graded`, `overdue`)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='student_id',
                in_=openapi.IN_QUERY,
                description='Talaba ID raqami bo‘yicha filtrlash',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='latest_only',
                in_=openapi.IN_QUERY,
                description='Agar `true` bo‘lsa, faqat har bir talabaning so‘nggi topshirishi qaytariladi',
                type=openapi.TYPE_BOOLEAN
            ),
        ],
        responses={
            200: openapi.Response(
                description="Natijalar va statistika bilan muvaffaqiyatli javob",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'assignment': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'statistics': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total_students': openapi.Schema(type=openapi.TYPE_STRING, description="Jami talabalar soni"),
                                'submitted_count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Topshirilgan ishlar soni"),
                                'graded_count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Baholangan ishlar soni"),
                                'submission_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description="Topshirish foizi"),
                            }
                        ),
                        'submissions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            403: openapi.Response(description="Ko‘rish huquqi yo‘q"),
            404: openapi.Response(description="Topshiriq topilmadi")
        }
    )
    def get(self, request, pk):
        try:
            assignment = Assignment.objects.get(id=pk)
        except Assignment.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Topshiriq topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)

        is_teacher = assignment.created_by == request.user
        is_student = ReTrainingStudent.objects.filter(
            student__user=request.user,
            group=assignment.group,
            is_active=True
        ).exists()

        if not (is_teacher or is_student):
            return Response({
                'status': False,
                'message': 'Sizda ushbu topshiriq natijalarini ko‘rish huquqi yo‘q'
            }, status=status.HTTP_403_FORBIDDEN)

        submissions = AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student__student').order_by('-started_at')

        status_filter = request.query_params.get('status')
        if status_filter:
            submissions = submissions.filter(status=status_filter)

        student_id = request.query_params.get('student_id')
        if student_id:
            submissions = submissions.filter(student_id=student_id)
        elif is_student and not is_teacher:
            student = ReTrainingStudent.objects.filter(
                student__user=request.user,
                group=assignment.group,
                is_active=True
            ).first()
            submissions = submissions.filter(student=student)

        latest_only = request.query_params.get('latest_only', 'false').lower() == 'true'
        if latest_only:
            latest_map = {}
            for submission in submissions:
                sid = submission.student.id
                if sid not in latest_map or submission.attempt_number > latest_map[sid].attempt_number:
                    latest_map[sid] = submission
            submissions = list(latest_map.values())

        total_students = ReTrainingStudent.objects.filter(
            group=assignment.group,
            is_active=True
        ).count()

        submitted_count = len(submissions)
        graded_count = sum(1 for s in submissions if s.status == 'graded')
        submission_rate = (submitted_count / total_students * 100) if total_students > 0 else 0

        serializer = AssignmentSubmissionSerializer(submissions, many=True)

        return Response({
            'assignment': AssignmentSerializer(assignment).data,
            'statistics': {
                'total_students': total_students,
                'submitted_count': submitted_count,
                'graded_count': graded_count,
                'submission_rate': round(submission_rate, 2)
            },
            'submissions': serializer.data
        }, status=status.HTTP_200_OK)


class StudentResultsAPIView(APIView):
    """
    Talaba natijalarini olish API.
    """
    permission_classes = [IsAdminTeacherOrStudent]

    @swagger_auto_schema(
        operation_summary="Talaba natijalari",
        operation_description="Joriy talabaga oid barcha natijalarni filtrlash va statistika bilan olish imkoniyati.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_QUERY,
                description='Topshirish ID — agar ko‘rsatilsa, faqat shu natija qaytariladi',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='group',
                in_=openapi.IN_QUERY,
                description='Filtrlash uchun guruh ID raqami',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='type',
                in_=openapi.IN_QUERY,
                description='Topshiriq turi: test yoki assignment',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='status',
                in_=openapi.IN_QUERY,
                description='Topshirish statusi (completed, graded va boshqalar)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='best_only',
                in_=openapi.IN_QUERY,
                description='Agar true bo‘lsa, har bir topshiriq bo‘yicha faqat eng yaxshi natija qaytariladi',
                type=openapi.TYPE_BOOLEAN
            ),
        ],
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli javob",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'statistics': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total_assignments': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                    description="Jami topshiriqlar soni"),
                                'completed_count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                  description="Bajarilgan topshiriqlar soni"),
                                'graded_count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                               description="Baholangan topshiriqlar soni"),
                                'passed_count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                               description="O‘tgan topshiriqlar soni"),
                                'average_grade': openapi.Schema(type=openapi.TYPE_NUMBER, description="O‘rtacha baho"),
                                'completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                  description="Bajarilish foizi"),
                                'pass_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description="O‘tish foizi"),
                            }
                        ),
                        'submissions': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Items(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            404: openapi.Response(description="Talaba topilmadi yoki guruhlarga ro‘yxatdan o‘tmagan")
        }
    )
    def get(self, request):
        """Joriy talabaning natijalarini olish yoki bitta natijani ko‘rish"""

        retraining_students = ReTrainingStudent.objects.filter(
            student__user=request.user,
            is_active=True
        ).select_related('group')

        if not retraining_students.exists():
            return Response({
                'status': False,
                'message': 'Siz qayta o‘qitish guruhlaridan birortasiga ro‘yxatdan o‘tmagansiz'
            }, status=status.HTTP_404_NOT_FOUND)

        # ---- NEW PART: checking assignment ID ----
        assignment_id = request.query_params.get('id')
        if assignment_id:
            try:
                submission = AssignmentSubmission.objects.select_related(
                    'assignment', 'assignment__group'
                ).filter(
                    assignment_id=assignment_id,
                    student__in=retraining_students
                ).order_by('-started_at').first()
            except AssignmentSubmission.DoesNotExist:
                submission = None

            if not submission:
                return Response(
                    {'detail': 'Natija topilmadi yoki sizga tegishli emas'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = AssignmentSubmissionSerializer(submission)
            return Response({'submission': serializer.data}, status=status.HTTP_200_OK)
        # --------------------------------

        # Default behavior for list
        submissions = AssignmentSubmission.objects.filter(
            student__in=retraining_students
        ).select_related('assignment', 'assignment__group').order_by('-started_at')

        group_id = request.query_params.get('group')
        assignment_type = request.query_params.get('type')
        status_filter = request.query_params.get('status')

        if group_id:
            submissions = submissions.filter(assignment__group_id=group_id)
        if assignment_type:
            submissions = submissions.filter(assignment__assignment_type=assignment_type)
        if status_filter:
            submissions = submissions.filter(status=status_filter)

        best_only = request.query_params.get('best_only', 'false').lower() == 'true'
        if best_only:
            best_map = {}
            for s in submissions:
                a_id = s.assignment_id
                if a_id not in best_map or (s.grade or 0) > (best_map[a_id].grade or 0):
                    best_map[a_id] = s
            submissions = list(best_map.values())

        serializer = AssignmentSubmissionSerializer(submissions, many=True)

        total_assignments = Assignment.objects.filter(
            group__in=[rs.group for rs in retraining_students],
            status='active'
        ).count()

        graded = [s for s in submissions if s.status == 'graded']
        completed = [s for s in submissions if s.status in ['completed', 'graded']]
        passed = [s for s in graded if (s.grade or 0) >= 60]

        average_grade = round(
            sum(s.grade for s in graded if s.grade) / len(graded), 2
        ) if graded else None

        statistics = {
            'total_assignments': total_assignments,
            'completed_count': len(completed),
            'graded_count': len(graded),
            'passed_count': len(passed),
            'average_grade': average_grade,
            'completion_rate': round(len(completed) / total_assignments * 100, 2) if total_assignments else 0,
            'pass_rate': round(len(passed) / len(graded) * 100, 2) if graded else 0,
        }

        return Response({
            'statistics': statistics,
            'submissions': serializer.data
        }, status=status.HTTP_200_OK)


# class BulkGradeSubmissionsAPIView(APIView):
#     """
#     API для массового оценивания заданий.
#     """
#     permission_classes = [IsTeacher]
#
#     @swagger_auto_schema(
#         operation_summary="Массовое оценивание заданий",
#         operation_description="Позволяет оценить несколько сдач заданий одновременно. "
#                               "Можно задать одну и ту же оценку и комментарий для всех.",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=["submission_ids", "grade"],
#             properties={
#                 "submission_ids": openapi.Schema(
#                     type=openapi.TYPE_ARRAY,
#                     items=openapi.Items(type=openapi.TYPE_INTEGER),
#                     description="Список ID сдач для оценивания"
#                 ),
#                 "grade": openapi.Schema(
#                     type=openapi.TYPE_NUMBER,
#                     format='float',
#                     description="Оценка от 0 до 100"
#                 ),
#                 "teacher_comment": openapi.Schema(
#                     type=openapi.TYPE_STRING,
#                     description="Комментарий преподавателя (необязательно)"
#                 )
#             }
#         ),
#         responses={
#             200: openapi.Response(
#                 description="Успешное массовое оценивание",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         "status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
#                         "message": openapi.Schema(type=openapi.TYPE_STRING),
#                         "updated_count": openapi.Schema(type=openapi.TYPE_INTEGER)
#                     }
#                 )
#             ),
#             400: "Ошибка валидации входных данных",
#             404: "Сдачи не найдены или уже оценены"
#         }
#     )
#     @transaction.atomic
#     def patch(self, request):
#         """Массово оценить задания"""
#         submission_ids = request.data.get('submission_ids', [])
#         grade = request.data.get('grade')
#         teacher_comment = request.data.get('teacher_comment', '')
#
#         if not submission_ids:
#             return Response({
#                 'status': False,
#                 'message': 'Не указаны ID сдач для оценивания'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         if grade is None or not (0 <= grade <= 100):
#             return Response({
#                 'status': False,
#                 'message': 'Некорректная оценка (должна быть от 0 до 100)'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         submissions = AssignmentSubmission.objects.filter(
#             id__in=submission_ids,
#             assignment__created_by=request.user,
#             status='completed'
#         )
#
#         if not submissions.exists():
#             return Response({
#                 'status': False,
#                 'message': 'Сдачи не найдены или уже оценены'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         updated_count = submissions.update(
#             grade=grade,
#             teacher_comment=teacher_comment,
#             status='graded',
#             graded_at=timezone.now(),
#             graded_by=request.user
#         )
#
#         return Response({
#             'status': True,
#             'message': f'Оценено {updated_count} работ',
#             'updated_count': updated_count
#         }, status=status.HTTP_200_OK)


# class AssignmentCloneAPIView(APIView):
#     """
#     API для клонирования задания.
#     """
#     permission_classes = [IsTeacher, IsAdmin]
#
#     @swagger_auto_schema(
#         operation_summary="Клонировать задание",
#         operation_description="Создает копию задания (в статусе 'draft') вместе с вопросами и вариантами ответов (если задание — тест).",
#         manual_parameters=[
#             openapi.Parameter(
#                 name='pk',
#                 in_=openapi.IN_PATH,
#                 description='ID оригинального задания',
#                 type=openapi.TYPE_INTEGER,
#                 required=True
#             )
#         ],
#         responses={
#             201: openapi.Response(
#                 description="Задание успешно клонировано",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
#                         'message': openapi.Schema(type=openapi.TYPE_STRING),
#                         'data': openapi.Schema(type=openapi.TYPE_OBJECT)
#                     }
#                 )
#             ),
#             404: openapi.Response(description="Задание не найдено или нет доступа")
#         }
#     )
#     @transaction.atomic
#     def post(self, request, pk):
#         """Клонировать задание"""
#         try:
#             original_assignment = Assignment.objects.get(id=pk, created_by=request.user)
#         except Assignment.DoesNotExist:
#             return Response({
#                 'status': False,
#                 'message': 'Задание не найдено или у вас нет прав'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         new_assignment = Assignment.objects.create(
#             title=f"{original_assignment.title} (копия)",
#             description=original_assignment.description,
#             assignment_type=original_assignment.assignment_type,
#             group=original_assignment.group,
#             created_by=request.user,
#             start_datetime=original_assignment.start_datetime,
#             end_datetime=original_assignment.end_datetime,
#             duration_minutes=original_assignment.duration_minutes,
#             max_attempts=original_assignment.max_attempts,
#             assignment_file=original_assignment.assignment_file,
#             show_results_immediately=original_assignment.show_results_immediately,
#             randomize_questions=original_assignment.randomize_questions,
#             enable_proctoring=original_assignment.enable_proctoring,
#             status='draft'
#         )
#
#         if original_assignment.assignment_type == 'test':
#             original_questions = TestQuestion.objects.filter(
#                 assignment=original_assignment,
#                 is_active=True
#             ).prefetch_related('options')
#
#             for question in original_questions:
#                 new_question = TestQuestion.objects.create(
#                     assignment=new_assignment,
#                     question_text=question.question_text,
#                     question_type=question.question_type,
#                     order=question.order,
#                     points=question.points,
#                     correct_answer=question.correct_answer,
#                     is_required=question.is_required
#                 )
#
#                 for option in question.options.all():
#                     TestQuestionOption.objects.create(
#                         question=new_question,
#                         option_text=option.option_text,
#                         is_correct=option.is_correct,
#                         order=option.order
#                     )
#
#             new_assignment.question_count = new_assignment.questions.filter(is_active=True).count()
#             new_assignment.save()
#
#         serializer = AssignmentSerializer(new_assignment)
#         return Response({
#             'status': True,
#             'message': 'Задание успешно клонировано',
#             'data': serializer.data
#         }, status=status.HTTP_201_CREATED)


class AssignmentDetailAPIView(APIView):
    """
    Muayyan topshiriqni olish, yangilash yoki o‘chirish API.
    """
    permission_classes = [IsAdminTeacherOrStudent]

    def get_object(self, id):
        print("PK from URL:", id)
        return get_object_or_404(
            Assignment.objects.select_related('group', 'created_by')
            .prefetch_related('questions__options', 'submissions'),
            id=id
        )

    def check_student_access(self, assignment, user):
        return ReTrainingStudent.objects.filter(
            student__user=user,
            group=assignment.group,
            is_active=True
        ).first()

    @swagger_auto_schema(
        operation_summary="Topshiriqni olish",
        operation_description="Topshiriq haqida to‘liq ma’lumot qaytaradi. "
                              "Agar foydalanuvchi — talaba bo‘lsa, to‘g‘ri javoblar yashiriladi va urinishlar ko‘rsatiladi.",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH, description="Topshiriq ID raqami", type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: openapi.Response(description="Kirish huquqi yo‘q"),
            404: openapi.Response(description="Topshiriq topilmadi")
        }
    )
    def get(self, request, id):
        assignment = self.get_object(id)
        retraining_student = self.check_student_access(assignment, request.user)
        is_student = bool(retraining_student)

        if is_student:
            serializer = AssignmentSerializerForStudent(assignment)
            data = serializer.data

            attempts = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=retraining_student
            ).order_by('-attempt_number')

            data['student_attempts'] = AssignmentSubmissionSerializer(attempts, many=True).data
            data['can_attempt'] = attempts.count() < assignment.max_attempts and assignment.is_active
        else:
            serializer = AssignmentSerializer(assignment)
            data = serializer.data

        return Response({'status': True, 'data': data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Topshiriqni yangilash (PUT)",
        request_body=AssignmentSerializer,
        responses={
            200: openapi.Response(
                description="Yangilandi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: "Validatsiya xatosi",
            403: "Huquq yo‘q",
        }
    )
    def put(self, request, id):
        assignment = self.get_object(id)
        if assignment.created_by != request.user:
            return Response({'status': False, 'message': 'Sizda huquq yo‘q'}, status=403)

        if assignment.submissions.exists():
            return Response({'status': False, 'message': 'Topshiriqlar topshirilgan, tahrirlash taqiqlanadi'}, status=400)

        serializer = AssignmentSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True, 'message': 'Yangilandi', 'data': serializer.data})
        return Response({'status': False, 'errors': serializer.errors}, status=400)

    @swagger_auto_schema(
        operation_summary="Topshiriqni qisman yangilash (PATCH)",
        request_body=AssignmentSerializer,
        responses={
            200: "OK",
            400: "Validatsiya xatosi",
            403: "Huquq yo'q",
        }
    )
    def patch(self, request, id):
        assignment = self.get_object(id)
        if assignment.created_by != request.user:
            return Response({'status': False, 'message': 'Sizda huquq yo\'q'}, status=403)

        # Копируем данные запроса
        data = request.data.copy()

        # Добавляем статус из query parameters если он есть
        status_param = request.query_params.get('status')
        if status_param:
            data['status'] = status_param

        serializer = AssignmentSerializer(assignment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True, 'message': 'Yangilandi', 'data': serializer.data})
        return Response({'status': False, 'errors': serializer.errors}, status=400)

    @swagger_auto_schema(
        operation_summary="Topshiriqni o‘chirish",
        responses={
            204: openapi.Response(
                description="O‘chirildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "O‘chirib bo‘lmaydi: topshiriqlar topshirilgan",
            403: "Huquq yo‘q"
        }
    )
    def delete(self, request, id):
        assignment = self.get_object(id)
        if assignment.created_by != request.user:
            return Response({'status': False, 'message': 'Sizda huquq yo‘q'}, status=403)

        if assignment.submissions.exists():
            return Response({'status': False, 'message': 'O‘chirib bo‘lmaydi: topshiriqlar topshirilgan'}, status=400)

        assignment_title = assignment.title
        assignment.delete()

        return Response({
            'status': True,
            'message': f'Topshiriq «{assignment_title}» o‘chirildi'
        }, status=status.HTTP_204_NO_CONTENT)


class GradeSubmissionAPIView(APIView):
    """
    O‘qituvchi tomonidan topshiriqqa baho qo‘yish API.
    """
    permission_classes = [IsAdminOrTeacher]

    def get_object(self, pk):
        return get_object_or_404(
            AssignmentSubmission.objects.select_related('assignment', 'student__student'),
            pk=pk
        )

    @swagger_auto_schema(
        operation_summary="Topshiriq topshirilishini ko‘rish",
        operation_description="Topshirilgan topshiriq haqida to‘liq ma’lumot qaytaradi (fayl, izohlar, status va h.k.).",
        manual_parameters=[
            openapi.Parameter(
                name="pk", in_=openapi.IN_PATH,
                description="Topshirish (submission) ID raqami",
                type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli javob",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: openapi.Response(description="Kirish huquqi yo‘q")
        }
    )
    def get(self, request, pk):
        submission = self.get_object(pk)
        if submission.assignment.created_by != request.user:
            return Response({
                'status': False,
                'message': 'Sizda ushbu topshiriq topshirilishini ko‘rish huquqi yo‘q'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmissionDetailSerializer(submission)
        return Response({
            'status': True,
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary="Topshiriqqa baho qo‘yish",
        operation_description="O‘qituvchiga fayl bilan topshirilgan topshiriqqa baho va izoh qo‘yish imkonini beradi.",
        request_body=GradeSubmissionSerializer,
        responses={
            200: openapi.Response(
                description="Baho muvaffaqiyatli qo‘yildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: "Xatolik: noto‘g‘ri status, tur yoki baho qiymati",
            403: "Ushbu topshiriqqa baho qo‘yish huquqi yo‘q"
        }
    )
    def patch(self, request, pk):
        submission = self.get_object(pk)

        if submission.assignment.created_by != request.user:
            return Response({
                'status': False,
                'message': 'Sizda ushbu topshiriqqa baho qo‘yish huquqi yo‘q'
            }, status=status.HTTP_403_FORBIDDEN)

        if submission.assignment.assignment_type != 'assignment':
            return Response({
                'status': False,
                'message': 'Faqat fayl bilan topshirilgan topshiriqlarni baholash mumkin'
            }, status=status.HTTP_400_BAD_REQUEST)

        if submission.status != 'completed':
            return Response({
                'status': False,
                'message': 'Faqat yakunlangan topshiriqlarni baholash mumkin'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = GradeSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': False,
                'message': 'Validatsiya xatosi',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        grade = serializer.validated_data['grade']
        teacher_comment = serializer.validated_data.get('teacher_comment', '')

        if not (0 <= grade <= 100):
            return Response({
                'status': False,
                'message': 'Baho 0 dan 100 gacha bo‘lishi kerak'
            }, status=status.HTTP_400_BAD_REQUEST)

        submission.grade = grade
        submission.teacher_comment = teacher_comment
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.graded_by = request.user
        submission.save()

        return Response({
            'status': True,
            'message': 'Baho muvaffaqiyatli qo‘yildi',
            'data': AssignmentSubmissionSerializer(submission).data
        }, status=status.HTTP_200_OK)


class AssignmentStatisticsAPIView(APIView):
    """
    Muayyan topshiriq bo‘yicha statistika.
    """
    permission_classes = [IsAdminTeacherOrStudent]

    def get_object(self, pk):
        return get_object_or_404(
            Assignment.objects.select_related('group', 'created_by'),
            pk=pk
        )

    @swagger_auto_schema(
        operation_summary="Topshiriq bo‘yicha statistika olish",
        operation_description="Topshiriq bo‘yicha batafsil statistika qaytaradi: jami talabalar soni, o‘rtacha baho, "
                              "topshirish va o‘tish foizi, urinishlar, baholar taqsimoti va topshirmagan talabalar ro‘yxati.",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                in_=openapi.IN_PATH,
                description='Topshiriq ID raqami',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Statistika bilan muvaffaqiyatli javob",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: openapi.Response(description="Statistikaga kirish huquqi yo‘q"),
            404: openapi.Response(description="Topshiriq topilmadi")
        }
    )
    def get(self, request, pk):
        assignment = self.get_object(pk)

        if assignment.created_by != request.user:
            return Response({
                'status': False,
                'message': 'Sizda ushbu topshiriq statistikasi bilan tanishish huquqi yo‘q'
            }, status=status.HTTP_403_FORBIDDEN)

        total_students = ReTrainingStudent.objects.filter(
            group=assignment.group,
            is_active=True
        ).count()

        submissions = AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student__student')

        submitted_count = submissions.values('student').distinct().count()
        completed_count = submissions.filter(status__in=['completed', 'graded']).values('student').distinct().count()
        graded_count = submissions.filter(status='graded').count()

        graded_submissions = submissions.filter(status='graded', grade__isnull=False)
        average_score = (
            graded_submissions.aggregate(avg_grade=models.Avg('grade'))['avg_grade'] or 0
            if graded_submissions.exists() else 0
        )
        passed_count = graded_submissions.filter(grade__gte=60).count()
        pass_rate = (passed_count / graded_count * 100) if graded_count > 0 else 0

        attempt_stats = submissions.values('attempt_number').annotate(
            count=Count('id')
        ).order_by('attempt_number')

        grade_distribution = {}
        if graded_submissions.exists():
            grade_ranges = [
                (0, 40, 'Qoniqarsiz'),
                (40, 60, 'Qoniqarli'),
                (60, 80, 'Yaxshi'),
                (80, 100, 'A’lo')
            ]
            for min_grade, max_grade, label in grade_ranges:
                count = graded_submissions.filter(
                    grade__gte=min_grade,
                    grade__lt=max_grade if max_grade < 100 else 101
                ).count()
                grade_distribution[label] = count

        submissions_data = AssignmentSubmissionSerializer(
            submissions.order_by('-started_at'),
            many=True
        ).data

        submitted_student_ids = set(submissions.values_list('student_id', flat=True))
        all_students = ReTrainingStudent.objects.filter(
            group=assignment.group,
            is_active=True
        ).exclude(id__in=submitted_student_ids)

        not_submitted_students = [{
            'id': student.id,
            'name': student.student.full_name,
            'student_id': student.student.student_id_number
        } for student in all_students]

        statistics_data = {
            'assignment_info': {
                'id': assignment.id,
                'title': assignment.title,
                'type': assignment.assignment_type,
                'status': assignment.status,
                'max_attempts': assignment.max_attempts,
                'question_count': assignment.question_count if assignment.assignment_type == 'test' else None
            },
            'basic_stats': {
                'total_students': total_students,
                'submitted_count': submitted_count,
                'completed_count': completed_count,
                'graded_count': graded_count,
                'not_submitted_count': total_students - submitted_count,
                'average_score': round(average_score, 2),
                'pass_rate': round(pass_rate, 2)
            },
            'attempt_stats': list(attempt_stats),
            'grade_distribution': grade_distribution,
            'submissions': submissions_data,
            'not_submitted_students': not_submitted_students
        }

        return Response({
            'status': True,
            'data': statistics_data
        })



class StudentAssignmentListAPIView(APIView):
    """
    Joriy talaba uchun topshiriqlar ro‘yxati.
    """
    permission_classes = [IsStudent]

    @swagger_auto_schema(
        operation_summary="Talaba topshiriqlari ro‘yxati",
        operation_description=(
            "Talabaga mavjud bo‘lgan barcha topshiriqlar ro‘yxatini qaytaradi. "
            "Topshiriq turiga (`type`) va holatiga (`status=available` yoki `completed`) ko‘ra filtrlash mumkin."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="type",
                in_=openapi.IN_QUERY,
                description="Topshiriq turiga ko‘ra filtrlash (`test`, `assignment`)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name="status",
                in_=openapi.IN_QUERY,
                description="Holat bo‘yicha filtrlash: `available` (topshirish uchun mavjud) yoki `completed` (allaqachon topshirilgan)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli javob",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            403: openapi.Response(description="Foydalanuvchi talaba emas"),
            404: openapi.Response(description="Talaba hech bir guruhga yozilmagan")
        }
    )
    def get(self, request):
        """Joriy talaba uchun topshiriqlarni olish"""
        try:
            retraining_students = ReTrainingStudent.objects.filter(
                student__user=request.user,
                is_active=True
            ).select_related('group', 'student')
        except:
            return Response({
                'status': False,
                'message': 'Siz qayta o‘qish talabasi emassiz'
            }, status=status.HTTP_403_FORBIDDEN)

        if not retraining_students.exists():
            return Response({
                'status': False,
                'message': 'Siz qayta o‘qish guruhlaridan birortasiga yozilmagansiz'
            }, status=status.HTTP_404_NOT_FOUND)

        group_ids = [rs.group.id for rs in retraining_students]
        assignments = Assignment.objects.filter(
            group_id__in=group_ids,
            status__in=['published', 'active']
        ).select_related('group', 'created_by').order_by('-created_at')

        assignment_type = request.query_params.get('type', None)
        status_filter = request.query_params.get('status', None)

        if assignment_type:
            assignments = assignments.filter(assignment_type=assignment_type)

        if status_filter:
            if status_filter == 'available':
                now = timezone.now()
                assignments = assignments.filter(
                    start_datetime__lte=now,
                    end_datetime__gte=now,
                    status='active'
                )
            elif status_filter == 'completed':
                completed_assignment_ids = []
                for assignment in assignments:
                    retraining_student = next(
                        (rs for rs in retraining_students if rs.group == assignment.group),
                        None
                    )
                    if retraining_student and AssignmentSubmission.objects.filter(
                            assignment=assignment,
                            student=retraining_student,
                            status__in=['completed', 'graded']
                    ).exists():
                        completed_assignment_ids.append(assignment.id)

                assignments = assignments.filter(id__in=completed_assignment_ids)

        assignment_data = []
        for assignment in assignments:
            retraining_student = next(
                (rs for rs in retraining_students if rs.group == assignment.group),
                None
            )

            if retraining_student:
                submissions = AssignmentSubmission.objects.filter(
                    assignment=assignment,
                    student=retraining_student
                ).order_by('-attempt_number')

                assignment_info = AssignmentSerializer(assignment).data
                assignment_info['student_submissions'] = AssignmentSubmissionSerializer(
                    submissions, many=True
                ).data

                assignment_info['attempts_used'] = submissions.count()
                assignment_info['attempts_left'] = assignment.max_attempts - submissions.count()
                assignment_info['can_submit'] = (
                        assignment.is_active and
                        submissions.count() < assignment.max_attempts
                )

                best_submission = submissions.filter(
                    status__in=['completed', 'graded'],
                    grade__isnull=False
                ).order_by('-grade').first()

                assignment_info['best_grade'] = best_submission.grade if best_submission else None
                assignment_info['is_passed'] = bool(best_submission and best_submission.grade >= 60)

                assignment_info['student_status'] = submissions.first().status if submissions.exists() else 'boshlanmagan'

                assignment_data.append(assignment_info)

        return Response({
            'status': True,
            'count': len(assignment_data),
            'data': assignment_data
        })


class ReTrainingGroupStartMeetingAPIView(APIView):
    permission_classes = [IsAdminOrTeacher]

    @swagger_auto_schema(
        operation_summary="Guruh uchun onlayn xonani yaratish",
        operation_description="Ko‘rsatilgan guruh uchun BigBlueButton xonasi yaratiladi, agar u hali yaratilmagan bo‘lsa. "
                              "Meeting ID, parollar va kirish URL manzilini qaytaradi.",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                description='Qayta o‘qish guruhi ID raqami',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli javob",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'room_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'meeting_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'attendeePW': openapi.Schema(type=openapi.TYPE_STRING),
                        'moderatorPW': openapi.Schema(type=openapi.TYPE_STRING),
                        'join_url': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(description="Guruh topilmadi")
        }
    )
    def post(self, request, pk):
        group = get_object_or_404(ReTrainingGroup, pk=pk)

        if group.online_room:
            return Response({
                'status': False,
                'message': 'Xona allaqachon yaratilgan',
                'room_id': str(group.online_room.meetingID)
            })

        count_users = group.retraining_students.filter(is_active=True).count()
        bbb_room = Bigbluebutton_Model()
        bbb_room.add_random_field(name=group.name, count_user=count_users)
        bbb_room.save()

        group.online_room = bbb_room
        group.save()

        return Response({
            'status': True,
            'message': 'Xona muvaffaqiyatli yaratildi',
            'meeting_id': str(bbb_room.meetingID),
            'attendeePW': bbb_room.attendeePW,
            'moderatorPW': bbb_room.moderatorPW,
            'join_url': f"{bbb_room.logoutURL}?meetingID={bbb_room.meetingID}"
        }, status=status.HTTP_200_OK)


class ExportAssignmentStatisticsPDFAPIView(APIView):
    """
    Topshiriq statistikasi PDF eksporti
    """
    permission_classes = [IsAdminOrTeacher]

    @swagger_auto_schema(
        operation_summary="Topshiriq statistikasi PDF formatida",
        operation_description="Tanlangan topshiriq bo‘yicha statistika hisobotini PDF formatida yuklab olish imkonini beradi.",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                in_=openapi.IN_PATH,
                description="Topshiriq ID raqami",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: "PDF fayl",
            404: "Topshiriq topilmadi"
        }
    )
    def get(self, request, pk):
        assignment = get_object_or_404(
            Assignment.objects.select_related('group'),
            pk=pk
        )
        submissions = AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student__student', 'student__group')

        # Guruh bo‘yicha ajratish
        grouped_data = defaultdict(list)
        for submission in submissions:
            group_name = submission.student.group.name if submission.student.group else "Guruhsiz"
            grouped_data[group_name].append(submission)

        # PDF yaratish
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Logo yuklash
        try:
            logo_path = "static/logo.png"
            logo = utils.ImageReader(logo_path)
            c.drawImage(logo, width - 5 * cm, height - 3 * cm, width=4 * cm, preserveAspectRatio=True)
        except Exception as e:
            print(f"[!] Logo yuklashda xatolik: {e}")

        # Sarlavha
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2.5 * cm, f"Topshiriq statistikasi: {assignment.title}")

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, height - 3.5 * cm, f"Yaratilgan sana: {assignment.created_at.strftime('%d.%m.%Y')}")
        c.drawString(2 * cm, height - 4.0 * cm, f"Turi: {assignment.assignment_type}")
        c.drawString(2 * cm, height - 4.5 * cm, f"Holati: {assignment.status}")
        c.drawString(2 * cm, height - 5.0 * cm, f"Hisobot vaqti: {timezone.now().strftime('%d.%m.%Y %H:%M')}")

        y = height - 6 * cm

        for group_name, group_submissions in grouped_data.items():
            if y < 5 * cm:
                c.showPage()
                y = height - 3 * cm

            c.setFont("Helvetica-Bold", 12)
            c.drawString(2 * cm, y, f"Guruh: {group_name}")
            y -= 0.7 * cm

            # Jadval sarlavhalari
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2 * cm, y, "F.I.O")
            c.drawString(7 * cm, y, "Holati")
            c.drawString(10 * cm, y, "Urinishlar soni")
            c.drawString(12 * cm, y, "Baho")
            c.drawString(14 * cm, y, "Foiz")
            y -= 0.4 * cm

            c.setFont("Helvetica", 10)
            for s in group_submissions:
                student = s.student.student
                full_name = getattr(student, 'full_name', f"{student.first_name} ").strip()
                c.drawString(2 * cm, y, full_name)
                c.drawString(7 * cm, y, s.status)
                c.drawString(10 * cm, y, str(s.attempt_number))
                c.drawString(12 * cm, y, f"{round(s.grade or 0, 2):.2f}")
                c.drawString(14 * cm, y, f"{round(s.percentage_score or 0, 1):.1f}%")
                y -= 0.4 * cm

                # Yangi sahifa
                if y < 3 * cm:
                    c.showPage()
                    y = height - 3 * cm

            y -= 0.5 * cm  # Guruhdan keyin bo‘sh joy

        c.save()
        buffer.seek(0)
        filename = f"topshiriq_statistikasi_{assignment.id}_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)


class TextTestQuestionsAPIView(APIView):
    """
    CRUD-операции для вопросов текстового теста.
    POST: Добавление/перезапись вопросов к Assignment (через TextTestCreateSerializer).
    GET: Получение списка вопросов Assignment.
    PUT: Обновление существующих вопросов.
    DELETE: Удаление всех вопросов теста.
    """
    permission_classes = [IsAdminOrTeacher]

    def check_test_creation_allowed(self, assignment):
        """
        Проверяет, можно ли добавлять/изменять тест к заданию.
        Тест можно добавлять/изменять только если статус задания не 'active' и 'published'
        """
        if assignment.status in ['active', 'published']:
            return False, f"Test savollarini qo'shish/o'zgartirish mumkin emas. Topshiriq statusi: '{assignment.status}'"
        return True, ""

    # --- GET METHOD ---
    @swagger_auto_schema(
        operation_summary="Test savollarini olish",
        operation_description="Berilgan Assignment ID bo'yicha test savollari va javoblarini qaytaradi.",
        manual_parameters=[
            openapi.Parameter(
                name="assignment_id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "assignment_id": openapi.Schema(type=openapi.TYPE_STRING),
                    "total_questions": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "assignment_status": openapi.Schema(type=openapi.TYPE_STRING),
                    "questions": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                }
            ),
            404: "Assignment topilmadi"
        }
    )
    def get(self, request, assignment_id):
        """
        Получает все вопросы и опции для указанного Assignment.
        """
        # 1️⃣ Ищем Assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)

        # 2️⃣ Извлекаем все вопросы, связанные с этим Assignment
        questions = TestQuestion.objects.filter(assignment=assignment).prefetch_related('options')

        # 3️⃣ Сериализуем вопросы для вывода
        try:
            serializer = TestQuestionRetrieveSerializer(questions, many=True)

            return Response({
                "status": True,
                "assignment_id": assignment.id,
                "assignment_status": assignment.status,
                "total_questions": len(questions),
                "questions": serializer.data
            }, status=status.HTTP_200_OK)

        except NameError:
            return Response({
                "status": False,
                "message": "TestQuestionRetrieveSerializer topilmadi. Uni yaratishingiz kerak."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- POST METHOD ---
    @swagger_auto_schema(
        operation_summary="Test savollarini yuklash",
        operation_description="O'qituvchi mavjud topshiriqqa savollar matnini yuklaydi. Faqat draft holatidagi topshiriqlarga savol qo'shish mumkin.",
        manual_parameters=[
            openapi.Parameter(
                name="assignment_id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        request_body=TextTestCreateSerializer,
        responses={
            201: "Savollar muvaffaqiyatli yaratildi",
            400: "Xatolik",
            403: "Ruxsat yo'q (topshiriq aktiv holatda)"
        }
    )
    def post(self, request, assignment_id):
        """
        Добавление новых вопросов теста.
        """
        # 1️⃣ Ищем Assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)

        # 2️⃣ Проверяем, можно ли добавлять тест
        is_allowed, message = self.check_test_creation_allowed(assignment)
        if not is_allowed:
            return Response({
                "status": False,
                "message": message
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ Проверяем, есть ли уже вопросы у этого задания
        existing_questions = TestQuestion.objects.filter(assignment=assignment)
        if existing_questions.exists():
            return Response({
                "status": False,
                "message": "Bu topshiriqqa allaqachon test savollari qo'shilgan. Yangi savol qo'shish uchun avval mavjud savollarni o'chiring yoki PUT metodidan foydalaning.",
                "existing_questions_count": existing_questions.count()
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4️⃣ Создаем вопросы
        serializer = TextTestCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment
            }
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                assignment = serializer.save()

            return Response({
                "status": True,
                "message": f"{assignment.question_count} ta savol muvaffaqiyatli yaratildi",
                "assignment_id": assignment.id,
                "assignment_status": assignment.status
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": False,
                "message": f"Saqlashda xatolik: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    # --- PUT METHOD ---
    @swagger_auto_schema(
        operation_summary="Test savollarini yangilash",
        operation_description="Mavjud test savollarini yangilash. Faqat draft holatidagi topshiriqlarni yangilash mumkin.",
        manual_parameters=[
            openapi.Parameter(
                name="assignment_id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        request_body=TextTestCreateSerializer,
        responses={
            200: "Savollar muvaffaqiyatli yangilandi",
            400: "Xatolik",
            404: "Savollar topilmadi"
        }
    )
    def put(self, request, assignment_id):
        """
        Полное обновление всех вопросов теста.
        """
        # 1️⃣ Ищем Assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)

        # 2️⃣ Проверяем, можно ли обновлять тест
        is_allowed, message = self.check_test_creation_allowed(assignment)
        if not is_allowed:
            return Response({
                "status": False,
                "message": message
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ Проверяем, есть ли вопросы для обновления
        existing_questions = TestQuestion.objects.filter(assignment=assignment)
        if not existing_questions.exists():
            return Response({
                "status": False,
                "message": "Yangilash uchun savollar topilmadi. Avval POST metodi orqali savol qo'shing."
            }, status=status.HTTP_404_NOT_FOUND)

        # 4️⃣ Удаляем старые вопросы и создаем новые
        serializer = TextTestCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment
            }
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                # Удаляем все существующие вопросы и их варианты ответов
                existing_questions.delete()

                # Создаем новые вопросы
                assignment = serializer.save()

            return Response({
                "status": True,
                "message": f"Test savollari muvaffaqiyatli yangilandi. {assignment.question_count} ta yangi savol yaratildi",
                "assignment_id": assignment.id,
                "assignment_status": assignment.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "message": f"Yangilashda xatolik: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    # --- PATCH METHOD ---
    @swagger_auto_schema(
        operation_summary="Test savollarini qisman yangilash",
        operation_description="Mavjud test savollariga yangi savollar qo'shish.",
        manual_parameters=[
            openapi.Parameter(
                name="assignment_id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        request_body=TextTestCreateSerializer,
        responses={
            200: "Yangi savollar muvaffaqiyatli qo'shildi",
            400: "Xatolik"
        }
    )
    def patch(self, request, assignment_id):
        """
        Добавление новых вопросов к существующим.
        """
        # 1️⃣ Ищем Assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)

        # 2️⃣ Проверяем, можно ли добавлять тест
        is_allowed, message = self.check_test_creation_allowed(assignment)
        if not is_allowed:
            return Response({
                "status": False,
                "message": message
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ Создаем дополнительные вопросы
        serializer = TextTestCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment
            }
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                # Сохраняем новые вопросы (старые остаются)
                assignment = serializer.save()

            # Получаем общее количество вопросов
            total_questions = TestQuestion.objects.filter(assignment=assignment).count()

            return Response({
                "status": True,
                "message": f"Yangi {assignment.question_count} ta savol muvaffaqiyatli qo'shildi. Jami savollar: {total_questions}",
                "assignment_id": assignment.id,
                "total_questions": total_questions,
                "assignment_status": assignment.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "message": f"Qo'shishda xatolik: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE METHOD ---
    @swagger_auto_schema(
        operation_summary="Barcha test savollarini o'chirish",
        operation_description="Berilgan Assignment ID bo'yicha barcha test savollarini va javob variantlarini o'chiradi. Faqat draft holatidagi topshiriqlardan o'chirish mumkin.",
        manual_parameters=[
            openapi.Parameter(
                name="assignment_id",
                in_=openapi.IN_PATH,
                description="Assignment ID",
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: "Barcha savollar o'chirildi",
            400: "Xatolik",
            404: "Savollar topilmadi"
        }
    )
    def delete(self, request, assignment_id):
        """
        Удаление всех вопросов теста.
        """
        # 1️⃣ Ищем Assignment
        assignment = get_object_or_404(Assignment, id=assignment_id)

        # 2️⃣ Проверяем, можно ли удалять тест
        is_allowed, message = self.check_test_creation_allowed(assignment)
        if not is_allowed:
            return Response({
                "status": False,
                "message": message
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ Проверяем, есть ли вопросы для удаления
        existing_questions = TestQuestion.objects.filter(assignment=assignment)
        if not existing_questions.exists():
            return Response({
                "status": False,
                "message": "O'chirish uchun savollar topilmadi"
            }, status=status.HTTP_404_NOT_FOUND)

        # 4️⃣ Удаляем все вопросы
        try:
            with transaction.atomic():
                questions_count = existing_questions.count()
                existing_questions.delete()

                # Обновляем счетчик вопросов в задании (если есть такое поле)
                if hasattr(assignment, 'question_count'):
                    assignment.question_count = 0
                    assignment.save(update_fields=['question_count'])

            return Response({
                "status": True,
                "message": f"{questions_count} ta savol muvaffaqiyatli o'chirildi",
                "assignment_id": assignment.id,
                "deleted_questions_count": questions_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "message": f"O'chirishda xatolik: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
