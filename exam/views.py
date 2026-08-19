import os

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Count, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers, generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from autoproctor.models import ScreenModel
from config.permissions import AllowOnlyTrustedOrigins
from group.models import Group
from shared.permissions import IsAdmin, IsAdminOrStudent, IsStudent
from students.models import Student
from .filters import ExamListFilter
from .models import (
    Exam,
    Question,
    Answer,
    Result,
    StudentExamAnswer,
    ExamStudent,
    StudentForTest
)
from .random_question import get_random_questions, get_random_questions_count
from .serializer import (
    ExamSerializer,
    ExamGroupUpdateSerializer,
    ExamStatusSerializer,
    ExamListGetSerializer,
    ExamUpdateSerializer,
    QuestionSerializer,
    QASerializer,
    ResultSerializer,
    ResultListSerializer,
    StudentExamAnswerSerializer,
    ExamDeleteGroupUpdateSerializer,
    ExamStudentForStatusSerializer,
    QuestionUpdateSerializer,
    QuestionDetailGetSerializer,
    ExamStudentListSerializer,
    ResultListForGroupSerializer, ResultUpdateSerializer, StudentForTestResultSerializer, SeansSerializer,
    QACreateSerializer, IsLogoutSerializer
)


class ExamCreateAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=ExamSerializer)
    def post(self, request, format=None, *args, **kwargs):
        attrs = request.data
        name = attrs.get('name')
        comment = attrs.get('comment')

        if name and Exam.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Bu imtihon allaqachon yaratilgan..."
                }
            )

        if comment and Exam.objects.filter(comment=comment).exists():
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Bu izoh allaqachon yaratilgan..."
                }
            )

        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            return Response(
                {
                    'status': True,
                    "message": "Imtihon muvaffaqiyatli yaratildi...",
                    "id": result.id
                }, status=status.HTTP_201_CREATED)
        return Response(
            {
                'status': False,
                "message": 'Imtihon yaratish muvaffaqiyatsiz tugadi...',
            }, status=status.HTTP_400_BAD_REQUEST)


class ExamGroupUpdateView(APIView):
    """
    View to update groups in an Exam instance.
    """
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=ExamGroupUpdateSerializer)
    def patch(self, request, id):
        try:
            exam = Exam.objects.get(id=id)
        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ExamGroupUpdateSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': "Muvaffaqiyatli qo'shildi..."
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDeleteGroupUpdateView(APIView):
    """
    View to update groups in an Exam instance.
    """
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=ExamDeleteGroupUpdateSerializer)
    def patch(self, request, id):
        try:
            exam = Exam.objects.get(id=id, status_action=True)
        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ExamDeleteGroupUpdateSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': "Muvaffaqiyatli o'chirildi..."
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamStatusApiView(APIView):
    """
    View to retrieve an Exam's status.
    """
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, pk):
        try:
            exam = Exam.objects.get(id=pk, status_action=True)
        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ExamStatusSerializer(exam)
        return Response(serializer.data)


class DetailExamApiView(APIView):
    """
    View to retrieve an Exam's status.
    """
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent ]

    def get(self, request, pk):
        try:
            exam = Exam.objects.get(id=pk, status_action=True)
        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ExamListGetSerializer(exam)
        return Response(serializer.data)


class QuestionGetListApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, exam):
        try:
            exam = Exam.objects.get(id=exam, status_action=True)
        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )

        questions = Question.objects.filter(exam=exam)
        serializer = QuestionDetailGetSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExamListsAPIView(generics.ListAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    serializer_class = ExamListGetSerializer
    queryset = Exam.objects.all()
    filterset_class = ExamListFilter


class ExamUpdateFullAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=ExamUpdateSerializer)
    def patch(self, request, pk):
        try:
            exam = Exam.objects.get(id=pk)
            questions = list(Question.objects.filter(is_active=True, exam_id=pk))
            if len(questions) < int(exam.total_count):
                return Response(
                    {
                        'status': False,
                        'message': 'Ushbu imtihonga tegishli savollar yetarli emas...'
                    },
                    status=status.HTTP_400_BAD_REQUEST)

        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "Imtihon faolligi sababli o'zgartish mumkin emas..."
                }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ExamUpdateSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': "Muvaffaqiyatli o'zgartirldi..."
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDeleteAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def delete(self, request, pk):
        try:
            exam = Exam.objects.get(id=pk)
        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )
        if exam.exam_status:
            return Response(
                {
                    'status': False,
                    'message': "Imtihon faolligi sababli o'chira olmaysiz..."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            exam.delete()
            return Response(
                {
                    'status': True,
                    'message': "Imtihon muvaffaqiyatli o'chirildi..."
                }, status=status.HTTP_204_NO_CONTENT
            )


class ExamStudentUpdateStatusAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=ExamStudentForStatusSerializer)
    def patch(self, request, pk, student_id):
        try:
            exam = Exam.objects.get(id=pk, status_action=True)
            exam_student = ExamStudent.objects.get(exam=exam, student_id=student_id)
        except Exam.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )
        except ExamStudent.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Ushbu imtihonga ushbu student biriktirilmagan...'
                }, status=status.HTTP_404_NOT_FOUND
            )

        if exam.exam_status:
            return Response(
                {
                    'status': False,
                    'message': "Imtihon faolligi sababli talabani faolligini o'zgartira olmaysiz..."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ExamStudentForStatusSerializer(exam_student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            autoproctor = ScreenModel.objects.filter(student_id=student_id, exam_id=pk).exists()
            if autoproctor:
                screen_models = ScreenModel.objects.filter(student_id=student_id, exam_id=pk)
                for screen_model in screen_models:
                    file_path = screen_model.image.path
                    screen_model.delete()
                    if os.path.exists(file_path):
                        os.remove(file_path)
            return Response(
                {
                    'status': True,
                    'message': "Muvaffaqiyatli o'zgartirldi..."
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=QuestionSerializer)
    def post(self, request, format=None):
        serializer = QuestionSerializer(data=request.data, many=True)
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            if int(result[-1].get('new_questions_count')) == 0:
                return Response(
                    {
                        'status': False,
                        'message': f"Test yaratilmadi, chunki barcha savollar takrorlandi..."
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {
                    'status': True,
                    'message': f"Muvaffaqiyatli yaratildi..."
                               f"Yangi savollar soni: {result[-1].get('new_questions_count')} ta, "
                               f"Takrorlangan savollar soni: {result[-1].get('duplicate_questions_count')} ta"
                }, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionUpdateAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=QuestionUpdateSerializer)
    def patch(self, request, format=None, pk=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Savol topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = QuestionUpdateSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            result = serializer.save()

            serialized_question = QuestionUpdateSerializer(result)

            return Response(
                {
                    'status': True,
                    'message': "Savol muvaffaqiyatli o'zgartirildi...",
                    'data': serialized_question.data
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionDetailGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, format=None, pk=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Savol topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )

        serialized_question = QuestionDetailGetSerializer(question)

        return Response(
            {
                'data': serialized_question.data
            }, status=status.HTTP_200_OK

        )


class QuestionDeleteAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def delete(self, request, format=None, pk=None):
        try:
            question = Question.objects.get(pk=pk, is_active=False)
        except Question.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "Savol faolligi uchun o'chirib bo'lmaydi..."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        question.delete()

        return Response(
            {
                'status': True,
                'message': "Savol muvaffaqiyatli o'chirildi..."
            }, status=status.HTTP_200_OK
        )


class CheckContinue(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent, ]

    @swagger_auto_schema(request_body=QACreateSerializer)
    def post(self, request, *args, **kwargs):
        attrs = request.data
        student_id = attrs.get('student')
        exam_id = attrs.get('exam')
        ip_address = attrs.get('ip_address')

        exam_student = ExamStudent.objects.filter(exam_id=exam_id, student_id=student_id)
        result_student = Result.objects.filter(exam_id=exam_id, student_id=student_id)

        try:
            exam = Exam.objects.get(exam_status=True, id=exam_id)
        except ObjectDoesNotExist:
            return Response(
                {'status': False, 'message': 'Imtihon topilmadi yoki imtihon faol emas...'},
                status=status.HTTP_404_NOT_FOUND
            )

        if exam.total_count in {None, 0}:
            return Response(
                {'status': False, 'message': "Imtihonda savollar soni to'g'ri kiritilmagan..."},
                status=status.HTTP_404_NOT_FOUND
            )

        if exam_student.exists():
            exam_student = exam_student.first()
            if exam_student.is_finish:
                return Response(
                    {'status': False, 'message': "Siz ushbu imtihonni allaqachon topshirib bo'lgansiz..."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if exam_student.is_login:
                return Response(
                    {'status': False, 'message': "Boshqa qurilmadan ishlanmoqda..."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not exam_student.is_login:
                if result_student.exists():
                    result_student = result_student.first()
                    if result_student.ip_address == ip_address or result_student.ip_address is None:
                        return Response(
                            {
                                'status': True
                            },
                            status=status.HTTP_200_OK
                        )
                    if result_student.ip_address != ip_address:
                        return Response(
                            {'status': False, 'message': "Boshqa qurilmadan ishlanmoqda..."},
                            status=status.HTTP_400_BAD_REQUEST
                        )


class TexnikAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=SeansSerializer)
    def post(self, request, *args, **kwargs):
        attrs = request.data
        exam_id = attrs.get('exam_id')

        exam_student = ExamStudent.objects.filter(exam_id=exam_id)

        try:
            exam = Exam.objects.get(exam_status=True, id=exam_id)
        except ObjectDoesNotExist:
            return Response(
                {'status': False, 'message': 'Imtihon topilmadi yoki imtihon faol emas...'},
                status=status.HTTP_404_NOT_FOUND
            )

        if exam.total_count in {None, 0}:
            return Response(
                {'status': False, 'message': "Imtihonda savollar soni to'g'ri kiritilmagan..."},
                status=status.HTTP_404_NOT_FOUND
            )

        if exam_student.exists():
            ExamStudent.objects.filter(exam_id=exam_id).update(is_login=False)

            return Response(
                {
                    'status': True,
                    'message': 'Muvaffaqiyatli bajarildi.'
                }
            )


class IsLogoutApiView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]

    @swagger_auto_schema(request_body=IsLogoutSerializer)
    def post(self, request, *args, **kwargs):
        attrs = request.data
        student_id = attrs.get('student')
        exam_id = attrs.get('exam')

        exam_student = ExamStudent.objects.filter(exam_id=exam_id, student_id=student_id)
        if exam_student.exists():
            exam_student = exam_student.first()
            exam_student.is_login = False
            exam_student.save()

            return Response(
                {
                    'status': True
                },
                status=status.HTTP_200_OK
            )


class QAAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent, ]

    @swagger_auto_schema(request_body=QACreateSerializer)
    def post(self, request, *args, **kwargs):
        attrs = request.data
        student_id = attrs.get('student')
        exam_id = attrs.get('exam')
        ip_address = attrs.get('ip_address')

        exam_student = ExamStudent.objects.filter(exam_id=exam_id, student_id=student_id)
        result_student = Result.objects.filter(exam_id=exam_id, student_id=student_id)
        student_for_test = StudentForTest.objects.filter(exam_id=exam_id, student_id=student_id)
        student_for_exam_answer = StudentExamAnswer.objects.filter(exam_id=exam_id, student_id=student_id)

        try:
            exam = Exam.objects.get(exam_status=True, id=exam_id)
        except ObjectDoesNotExist:
            return Response(
                {'status': False, 'message': 'Imtihon topilmadi yoki imtihon faol emas...'},
                status=status.HTTP_404_NOT_FOUND
            )

        if exam.total_count in {None, 0}:
            return Response(
                {'status': False, 'message': "Imtihonda savollar soni to'g'ri kiritilmagan..."},
                status=status.HTTP_404_NOT_FOUND
            )

        if exam_student.exists():
            exam_student = exam_student.first()
            if exam_student.is_finish:
                return Response(
                    {'status': False, 'message': "Siz ushbu imtihonni allaqachon topshirib bo'lgansiz..."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if exam_student.is_login:
                if result_student.exists():
                    result_student = result_student.first()
                    if result_student.ip_address:
                        if result_student.ip_address == ip_address:
                            if student_for_test.exists():
                                json_field_data = student_for_test[0].json_field
                                if not student_for_exam_answer.exists():
                                    for frontend_question in json_field_data:
                                        question_id = frontend_question['id']

                                        try:
                                            question = Question.objects.get(id=question_id)
                                        except Question.DoesNotExist:
                                            return Response(
                                                {
                                                    'status': True,
                                                    'message': f'Question with id {question} not found.'
                                                },
                                                status=status.HTTP_404_NOT_FOUND)

                                        try:
                                            answer = Answer.objects.get(question=question, isTrue=True)
                                        except Answer.DoesNotExist:
                                            return Response(
                                                {
                                                    'status': False,
                                                    'message': f'True answer with id not found for question {question}.'
                                                },
                                                status=status.HTTP_404_NOT_FOUND)

                                        student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                            exam_id=exam_id,
                                            student_id=student_id,
                                            question=question,
                                            defaults={'true_answer': answer}
                                        )

                                        if not created:
                                            student_exam_answer.true_answer = answer
                                            student_exam_answer.save()

                                return Response(
                                    json_field_data,
                                    status=status.HTTP_200_OK
                                )

                            else:
                                random_questions = get_random_questions(int(exam.total_count), exam_id=exam_id)
                                random_questions_count = get_random_questions_count(exam_id=exam_id)
                                if not random_questions or random_questions_count < int(exam.total_count):
                                    return Response(
                                        {
                                            'status': False,
                                            'message': 'Ushbu imtihonga tegishli savollar topilmadi yoki yetarli emas...'
                                        },
                                        status=status.HTTP_400_BAD_REQUEST)
                                serializer = QASerializer(random_questions, many=True)
                                try:
                                    StudentForTest.objects.create(exam_id=exam_id, student_id=student_id,
                                                                  json_field=serializer.data)

                                    for frontend_question in serializer.data:
                                        question_id = frontend_question['id']

                                        try:
                                            question = Question.objects.get(id=question_id)
                                        except Question.DoesNotExist:
                                            return Response(
                                                {'status': False,
                                                 'message': f'Question with id {question_id} not found.'},
                                                status=status.HTTP_404_NOT_FOUND
                                            )

                                        try:
                                            answer = Answer.objects.get(question=question, isTrue=True)
                                        except Answer.DoesNotExist:
                                            return Response(
                                                {'status': False,
                                                 'message': f'True answer not found for question {question_id}.'},
                                                status=status.HTTP_404_NOT_FOUND
                                            )

                                        student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                            exam_id=exam_id,
                                            student_id=student_id,
                                            question=question,
                                            defaults={'true_answer': answer}
                                        )

                                        if not created:
                                            student_exam_answer.true_answer = answer
                                            student_exam_answer.save()

                                        exam_student.is_login = True
                                        exam_student.save()

                                    return Response(serializer.data, status=status.HTTP_200_OK)

                                except Exception as e:
                                    return Response(
                                        {'status': False,
                                         'message': "Imtihon savollarini saqlashda xatolik yuz berdi..."},
                                        status=status.HTTP_409_CONFLICT
                                    )

                        else:
                            return Response(
                                {'status': False, 'message': "Boshqa qurilmadan ishlanmoqda..."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                    if result_student.ip_address is None:
                        if student_for_test.exists():
                            json_field_data = student_for_test[0].json_field
                            if not student_for_exam_answer.exists():
                                for frontend_question in json_field_data:
                                    question_id = frontend_question['id']

                                    try:
                                        question = Question.objects.get(id=question_id)
                                    except Question.DoesNotExist:
                                        return Response(
                                            {
                                                'status': True,
                                                'message': f'Question with id {question} not found.'
                                            },
                                            status=status.HTTP_404_NOT_FOUND)

                                    try:
                                        answer = Answer.objects.get(question=question, isTrue=True)
                                    except Answer.DoesNotExist:
                                        continue

                                    student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                        exam_id=exam_id,
                                        student_id=student_id,
                                        question=question,
                                        defaults={'true_answer': answer}
                                    )

                                    if not created:
                                        student_exam_answer.true_answer = answer
                                        student_exam_answer.save()

                            return Response(
                                json_field_data,

                                status=status.HTTP_200_OK
                            )

                        else:
                            random_questions = get_random_questions(int(exam.total_count), exam_id=exam_id)
                            random_questions_count = get_random_questions_count(exam_id=exam_id)
                            if not random_questions or random_questions_count < int(exam.total_count):
                                return Response(
                                    {
                                        'status': False,
                                        'message': 'Ushbu imtihonga tegishli savollar topilmadi yoki yetarli emas...'
                                    },
                                    status=status.HTTP_400_BAD_REQUEST)
                            serializer = QASerializer(random_questions, many=True)
                            try:
                                StudentForTest.objects.create(exam_id=exam_id, student_id=student_id,
                                                              json_field=serializer.data)

                                for frontend_question in serializer.data:
                                    question_id = frontend_question['id']

                                    try:
                                        question = Question.objects.get(id=question_id)
                                    except Question.DoesNotExist:
                                        return Response(
                                            {'status': False,
                                             'message': f'Question with id {question_id} not found.'},
                                            status=status.HTTP_404_NOT_FOUND
                                        )

                                    try:
                                        answer = Answer.objects.get(question=question, isTrue=True)
                                    except Answer.DoesNotExist:
                                        return Response(
                                            {'status': False,
                                             'message': f'True answer not found for question {question_id}.'},
                                            status=status.HTTP_404_NOT_FOUND
                                        )

                                    student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                        exam_id=exam_id,
                                        student_id=student_id,
                                        question=question,
                                        defaults={'true_answer': answer}
                                    )

                                    if not created:
                                        student_exam_answer.true_answer = answer
                                        student_exam_answer.save()

                                    exam_student.is_login = True
                                    exam_student.save()

                                return Response(serializer.data, status=status.HTTP_200_OK)

                            except Exception as e:
                                return Response(
                                    {'status': False,
                                     'message': "Imtihon savollarini saqlashda xatolik yuz berdi..."},
                                    status=status.HTTP_409_CONFLICT
                                )

            if exam_student.is_login is False:
                if result_student.exists():
                    result_student = result_student.first()
                    if result_student.ip_address is None:
                        if student_for_test.exists():
                            json_field_data = student_for_test[0].json_field
                            if not student_for_exam_answer.exists():
                                for frontend_question in json_field_data:
                                    question_id = frontend_question['id']

                                    try:
                                        question = Question.objects.get(id=question_id)
                                    except Question.DoesNotExist:
                                        return Response(
                                            {
                                                'status': True,
                                                'message': f'Question with id {question} not found.'
                                            },
                                            status=status.HTTP_404_NOT_FOUND)

                                    try:
                                        answer = Answer.objects.get(question=question, isTrue=True)
                                    except Answer.DoesNotExist:
                                        return Response(
                                            {
                                                'status': False,
                                                'message': f'True answer with id not found for question {question}.'
                                            },
                                            status=status.HTTP_404_NOT_FOUND)

                                    student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                        exam_id=exam_id,
                                        student_id=student_id,
                                        question=question,
                                        defaults={'true_answer': answer}
                                    )

                                    if not created:
                                        student_exam_answer.true_answer = answer
                                        student_exam_answer.save()

                                    exam_student.is_login = True
                                    exam_student.save()

                            return Response(
                                json_field_data,

                                status=status.HTTP_200_OK
                            )

                        else:
                            random_questions = get_random_questions(int(exam.total_count), exam_id=exam_id)
                            random_questions_count = get_random_questions_count(exam_id=exam_id)
                            if not random_questions or random_questions_count < int(exam.total_count):
                                return Response(
                                    {
                                        'status': False,
                                        'message': 'Ushbu imtihonga tegishli savollar topilmadi yoki yetarli emas...'
                                    },
                                    status=status.HTTP_400_BAD_REQUEST)
                            serializer = QASerializer(random_questions, many=True)
                            try:
                                StudentForTest.objects.create(exam_id=exam_id, student_id=student_id,
                                                              json_field=serializer.data)

                                for frontend_question in serializer.data:
                                    question_id = frontend_question['id']

                                    try:
                                        question = Question.objects.get(id=question_id)
                                    except Question.DoesNotExist:
                                        return Response(
                                            {'status': False,
                                             'message': f'Question with id {question_id} not found.'},
                                            status=status.HTTP_404_NOT_FOUND
                                        )

                                    try:
                                        answer = Answer.objects.get(question=question, isTrue=True)
                                    except Answer.DoesNotExist:
                                        return Response(
                                            {'status': False,
                                             'message': f'True answer not found for question {question_id}.'},
                                            status=status.HTTP_404_NOT_FOUND
                                        )

                                    student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                        exam_id=exam_id,
                                        student_id=student_id,
                                        question=question,
                                        defaults={'true_answer': answer}
                                    )

                                    if not created:
                                        student_exam_answer.true_answer = answer
                                        student_exam_answer.save()

                                    exam_student.is_login = True
                                    exam_student.save()

                                return Response(serializer.data, status=status.HTTP_200_OK)

                            except Exception as e:
                                return Response(
                                    {'status': False,
                                     'message': "Imtihon savollarini saqlashda xatolik yuz berdi..."},
                                    status=status.HTTP_409_CONFLICT
                                )

                    if result_student.ip_address:
                        if result_student.ip_address == ip_address:
                            if student_for_test.exists():
                                json_field_data = student_for_test[0].json_field
                                if not student_for_exam_answer.exists():
                                    for frontend_question in json_field_data:
                                        question_id = frontend_question['id']

                                        try:
                                            question = Question.objects.get(id=question_id)
                                        except Question.DoesNotExist:
                                            return Response(
                                                {
                                                    'status': True,
                                                    'message': f'Question with id {question} not found.'
                                                },
                                                status=status.HTTP_404_NOT_FOUND)

                                        try:
                                            answer = Answer.objects.get(question=question, isTrue=True)
                                        except Answer.DoesNotExist:
                                            return Response(
                                                {
                                                    'status': False,
                                                    'message': f'True answer with id not found for question {question}.'
                                                },
                                                status=status.HTTP_404_NOT_FOUND)

                                        student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                            exam_id=exam_id,
                                            student_id=student_id,
                                            question=question,
                                            defaults={'true_answer': answer}
                                        )

                                        if not created:
                                            student_exam_answer.true_answer = answer
                                            student_exam_answer.save()
                                exam_student.is_login = True
                                exam_student.save()
                                return Response(
                                    json_field_data,

                                    status=status.HTTP_200_OK
                                )

                            else:
                                random_questions = get_random_questions(int(exam.total_count), exam_id=exam_id)
                                random_questions_count = get_random_questions_count(exam_id=exam_id)
                                if not random_questions or random_questions_count < int(exam.total_count):
                                    return Response(
                                        {
                                            'status': False,
                                            'message': 'Ushbu imtihonga tegishli savollar topilmadi yoki yetarli emas...'
                                        },
                                        status=status.HTTP_400_BAD_REQUEST)
                                serializer = QASerializer(random_questions, many=True)
                                try:
                                    StudentForTest.objects.create(exam_id=exam_id, student_id=student_id,
                                                                  json_field=serializer.data)

                                    for frontend_question in serializer.data:
                                        question_id = frontend_question['id']

                                        try:
                                            question = Question.objects.get(id=question_id)
                                        except Question.DoesNotExist:
                                            return Response(
                                                {'status': False,
                                                 'message': f'Question with id {question_id} not found.'},
                                                status=status.HTTP_404_NOT_FOUND
                                            )

                                        try:
                                            answer = Answer.objects.get(question=question, isTrue=True)
                                        except Answer.DoesNotExist:
                                            return Response(
                                                {'status': False,
                                                 'message': f'True answer not found for question {question_id}.'},
                                                status=status.HTTP_404_NOT_FOUND
                                            )

                                        student_exam_answer, created = StudentExamAnswer.objects.get_or_create(
                                            exam_id=exam_id,
                                            student_id=student_id,
                                            question=question,
                                            defaults={'true_answer': answer}
                                        )

                                        if not created:
                                            student_exam_answer.true_answer = answer
                                            student_exam_answer.save()

                                    exam_student.is_login = True
                                    exam_student.save()

                                    return Response(serializer.data, status=status.HTTP_200_OK)

                                except Exception as e:
                                    return Response(
                                        {'status': False,
                                         'message': "Imtihon savollarini saqlashda xatolik yuz berdi..."},
                                        status=status.HTTP_409_CONFLICT
                                    )

                        if result_student.ip_address != ip_address:
                            return Response(
                                {'status': False, 'message': "Boshqa qurilmadan ishlanmoqda..."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
        else:
            return Response(
                {'status': False, 'message': 'Imtihon boshlanmagan yoki mavjud emas...'},
                status=status.HTTP_404_NOT_FOUND
            )


class ResultList(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, format=None):
        results = Result.objects.all()
        serializer = ResultListSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResultListForGroup(APIView):
    serializer_class = ResultListForGroupSerializer
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, group_id, exam_id):
        queryset = ExamStudent.objects.filter(group_id=group_id, exam_id=exam_id)

        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Natija topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class ResultListForStudent(APIView):
    serializer_class = ResultListSerializer
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent, ]

    def get(self, request, student_id, exam_id):
        try:
            result_instance = Result.objects.get(student_id=student_id, exam_id=exam_id)
            serializer = self.serializer_class(result_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Result.DoesNotExist:
            response_data = {
                "status": False,
                "message": "Natija topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class ResultListForExam(APIView):
    serializer_class = ResultListSerializer
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, exam_id, *args, **kwargs):
        queryset = Result.objects.filter(exam_id=exam_id)

        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Natija topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class ExamListForStudent(APIView):
    serializer_class = ExamStudentListSerializer
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent]

    def get(self, request, student, *args, **kwargs):

        queryset = ExamStudent.objects.filter(student_id=student)

        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Sizda imtihonlar topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class ExamListForIsFinishStudent(APIView):
    serializer_class = ExamStudentListSerializer
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent]

    def get(self, request, student, *args, **kwargs):

        queryset = ExamStudent.objects.filter(student_id=student, is_finish=True)

        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Sizda imtihonlar topilmadi!"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class ResultCreateAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent, ]

    @swagger_auto_schema(request_body=ResultSerializer)
    def post(self, request, format=None):
        exam_id = request.data.get('exam')
        student_id = request.data.get('student')
        group_id = request.data.get('group')

        filter_params = {
            'exam_id': exam_id,
            'student_id': student_id,
            'group_id': group_id,
        }

        existing_result = Result.objects.filter(**filter_params).first()

        if existing_result:
            exam_time_second_value = existing_result.exam_time_second

            serializer = ResultSerializer(existing_result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = ResultSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                result = serializer.save()
                result.exam_time_second
                result.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentExamAnswerUpdateAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent]

    @swagger_auto_schema(request_body=StudentExamAnswerSerializer)
    def patch(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        exam_id = self.kwargs.get('exam_id')
        question_id = request.data.get('question')
        is_selected = request.data.get('is_selected')
        ip_address = request.data.get('ip_address')

        try:
            result_instance, created = Result.objects.get_or_create(
                exam_id=exam_id,
                student_id=student_id,
                defaults={'ip_address': ip_address}
            )

            if not created:
                result_instance.ip_address = ip_address
                result_instance.save()

            exam_answer = StudentExamAnswer.objects.get(
                exam_id=exam_id,
                student_id=student_id,
                question_id=question_id
            )

            try:
                selected_answer = Answer.objects.get(id=is_selected, question_id=question_id)
            except Answer.DoesNotExist:
                return Response(
                    {
                        'status': False,
                        'message': 'Selected answer not found for the question.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            exam_answer.is_selected = selected_answer
            exam_answer.save()

            selected_answers = StudentExamAnswer.objects.filter(
                exam_id=exam_id,
                student_id=student_id,
                is_selected__isnull=False
            )

            serializer = StudentExamAnswerSerializer(selected_answers, many=True)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except StudentExamAnswer.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Imtihon topilmadi...'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class CorrectAnswersCountAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent, ]

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        exam_id = self.kwargs.get('exam_id')

        total_questions_count = StudentExamAnswer.objects.filter(
            exam_id=exam_id,
            student_id=student_id
        ).count()

        correct_answers_count = StudentExamAnswer.objects.filter(
            exam_id=exam_id,
            student_id=student_id,
            is_selected=F('true_answer')
        ).aggregate(
            correct_count=Coalesce(Count('id'), Value(0))
        )['correct_count']

        student_for_result = Result.objects.filter(exam_id=exam_id, student_id=student_id)
        exam_student = ExamStudent.objects.filter(exam_id=exam_id, student_id=student_id)

        if student_for_result.exists():
            student_for_result = student_for_result.first()
            student_for_result.correct_answer = correct_answers_count
            student_for_result.end_time = timezone.now()
            student_for_result.time_spent = student_for_result.exam_time * 60 - student_for_result.exam_time_second
            student_for_result.save()

            if exam_student.exists():
                exam_student = exam_student.first()
                exam_student.is_finish = True
                exam_student.is_active = False
                exam_student.is_login = False
                exam_student.save()

        return Response(
            {
                'total_questions_count': total_questions_count,
                'correct_answers_count': correct_answers_count
            }, status=status.HTTP_200_OK)


# class ResultUpdateAPIView(APIView):
#
#     @swagger_auto_schema(request_body=ResultUpdateSerializer)
#     def patch(self, request, *args, **kwargs):
#         student_id = self.kwargs.get('student_id')
#         exam_id = self.kwargs.get('exam_id')
#
#         try:
#             result = Result.objects.get(
#                 exam_id=exam_id,
#                 student_id=student_id,
#             )
#
#             serializer = ResultUpdateSerializer(result, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#
#                 return Response(
#                     {
#                         'status': True,
#                         'message': "Natija muvaffaqiyatli o'zgartirildi...",
#                     }, status=status.HTTP_200_OK
#                 )
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#         except Result.DoesNotExist:
#             return Response(
#                 {
#                     'status': False,
#                     'message': 'Natija topilmadi...'
#                 },
#                 status=status.HTTP_404_NOT_FOUND
#             )


class IsSelectedAnswersAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent, ]

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        exam_id = self.kwargs.get('exam_id')

        selected_answers = StudentExamAnswer.objects.filter(
            exam_id=exam_id,
            student_id=student_id,
            is_selected__isnull=False
        )

        serializer = StudentExamAnswerSerializer(selected_answers, many=True)

        return Response(
            {
                'status': True,
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )


class IsStudentSelectedAnswersProfileAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent, ]

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        exam_id = self.kwargs.get('exam_id')

        student_for_result = ExamStudent.objects.filter(exam_id=exam_id, student_id=student_id)

        if student_for_result.exists():
            student_for_result = student_for_result.first()
            if student_for_result.is_finish:
                student_for_test_instance = StudentForTest.objects.filter(
                    exam_id=exam_id,
                    student_id=student_id,
                ).first()

                if student_for_test_instance:
                    serializer = StudentForTestResultSerializer(student_for_test_instance)
                    return Response(
                        {
                            'status': True,
                            'data': serializer.data
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    response_data = {
                        'status': False,
                        'message': 'Siz hali test yechishni boshlamagansiz...'
                    }
                    return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(
                    {
                        'status': False,
                        'message': 'Siz hali testni yakunlamagansiz...'
                    }, status=status.HTTP_404_NOT_FOUND)


class SeansDeleteAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    @swagger_auto_schema(request_body=SeansSerializer)
    def post(self, request, format=None):
        exam_id = request.data.get('exam_id')

        exam = Exam.objects.filter(id=exam_id)
        check_exam = exam.first()
        if exam.exists() and check_exam.exam_status:
            students = ExamStudent.objects.filter(exam_id=exam_id)
            if students.exists():
                for student in students:
                    if student.is_active and not student.is_finish:
                        result_student = Result.objects.filter(exam_id=exam_id, student_id=student.student.id)
                        if result_student.exists():
                            result_student = result_student.first()
                            result_student.ip_address = None
                            result_student.save()
                        else:
                            continue
                    else:
                        continue
                return Response(
                    {
                        'status': True,
                        'message': 'Muvaffaqiyatli bajarildi...'
                    }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'status': False,
                        'message': 'Ushbu imtihonni hali hech kim boshlamagan...'
                    }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {
                    'status': False,
                    'message': 'Bunaqa imtihon topilmadi yoki aktiv emas...'
                }, status=status.HTTP_404_NOT_FOUND)


class CheckAttemptsAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        exam_id = self.kwargs.get('exam_id')

        exam = Exam.objects.filter(id=exam_id).first()
        result = Result.objects.filter(exam_id=exam_id, student_id=student_id)
        exam_student = ExamStudent.objects.filter(exam_id=exam_id, student_id=student_id)
        student_exam_answer = StudentExamAnswer.objects.filter(exam_id=exam_id, student_id=student_id)
        student_for_test = StudentForTest.objects.filter(exam_id=exam_id, student_id=student_id)

        if result.exists():
            result_first = result.first()
            if int(result_first.attempts) < int(
                    exam.attempts) and exam.begin_time <= timezone.now() <= exam.end_time:
                try:
                    if exam_student.exists():
                        exam_student = exam_student.first()
                        exam_student.is_finish = False
                        exam_student.is_login = False
                        exam_student.save()

                    if student_exam_answer.exists():
                        student_exam_answer.delete()
                    if student_for_test.exists():
                        student_for_test.delete()

                    result.delete()
                except Exception as e:
                    print(f"Error in CheckAttemptsAPIView: {e}")
                return Response(
                    {'status': True},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'status': False},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'status': True},
                status=status.HTTP_200_OK
            )
