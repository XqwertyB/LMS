import datetime
import random

from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response

from group.models import Group
from group.serializers import GetGroupSerializer
from learning_process.serializers import (
    GetCurriculumSerializer,
    GetEducationyearSerializer
)
from semestr.serializers import GetHsemesterSerializer
from shared.serializers import ExamTypesSerializer
from students.models import Student
from students.serializers import StudentSerializer, StudentForResultSerializer
from subjects.serializers import GetSubjectSerializer
from .models import (
    Exam,
    Question,
    Answer,
    Result,
    StudentExamAnswer,
    ExamStudent, StudentForTest
)


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            'name', 'comment', 'curriculum', 'education_year',
            'semester', 'exam_type', 'exam_status', 'begin_time',
            'end_time', 'exam_time', 'max_score', 'attempts',
            'total_count', 'is_random', 'subject'
        ]

    def validate(self, data):
        current_datetime = timezone.now()

        name = data.get('name', None)
        comment = data.get('comment', None)
        begin_time = data.get('begin_time', None)
        end_time = data.get('end_time', None)
        max_score = data.get('max_score', None)
        attempts = data.get('attempts', None)
        total_count = data.get('attempts', None)

        if name is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Imtihon nomini kiritish majburiy..."
                }
            )

        if comment is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Imtihon uchun izoh kiritish majburiy..."
                }
            )

        if begin_time is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Imtihonni boshlanish vaqtini kiritish majburiy..."
                }
            )

        if begin_time < current_datetime:
            raise serializers.ValidationError({
                'status': False,
                "message": "Imtihon boshlanish vaqti joriy vaqtdan kichik bo'lishi mumkin emas"
            })

        if end_time is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Imtihonni tugash vaqtini kiritish majburiy..."
                }
            )
        if end_time < current_datetime:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Imtihon tugash vaqti joriy vaqtdan kichik bo'lishi mumkin emas"
                }
            )

        if not max_score:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Umumiy ballni kiritish majburiy..."
                }
            )

        if int(max_score) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Umumiy ball noto'g'ri kiritildi..."
                }
            )
        if not attempts:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Urinishlar maydonini kiritish majburiy..."
                }
            )

        if int(attempts) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Urinishlar qiymati noto'g'ri kiritildi..."
                }
            )

        if not total_count:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Savollar sonini kiritish majburiy..."
                }
            )

        if int(total_count) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Savollar soni qiymati noto'g'ri kiritildi..."
                }
            )

        return data


class ExamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            'name', 'comment', 'curriculum', 'education_year',
            'semester', 'exam_type', 'exam_status', 'begin_time',
            'end_time', 'exam_time', 'max_score', 'attempts',
            'total_count', 'subject'
        ]


class GetExamDetailSerializer(serializers.ModelSerializer):
    curriculum = GetCurriculumSerializer()
    education_year = GetEducationyearSerializer()
    semester = GetHsemesterSerializer()
    exam_type = ExamTypesSerializer()
    subject = GetSubjectSerializer()
    is_enabled = serializers.SerializerMethodField()

    def get_is_enabled(self, obj):
        try:
            exam = Exam.objects.get(id=obj.id)
            if exam.begin_time <= timezone.now() <= exam.end_time:
                return True
            else:
                return False
        except exam.DoesNotExist:
            return False

    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'comment', 'curriculum', 'education_year',
            'semester', 'exam_type', 'exam_status', 'begin_time',
            'end_time', 'exam_time', 'max_score', 'attempts',
            'total_count', 'subject', 'is_enabled'
        ]


class ExamGroupUpdateSerializer(serializers.ModelSerializer):
    group_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = Exam
        fields = ['group_ids']

    def update(self, instance, validated_data):
        group_ids = validated_data.get('group_ids', [])

        if instance.exam_status:
            raise serializers.ValidationError({
                'status': False,
                'message': "Imtihon faolligi sababli guruhni qo'sha olmaysiz..."
            })

        groups = Group.objects.filter(id__in=group_ids)
        if groups.count() != len(group_ids):
            raise serializers.ValidationError({
                'status': False,
                'message': "One or more specified groups do not exist."
            })

        for group_id in group_ids:
            students = Student.objects.filter(group_id=group_id)
            for student in students:
                try:
                    ExamStudent.objects.get_or_create(exam=instance, student=student, group_id=group_id,
                                                      defaults={'semester': student.semester, 'is_active': True})
                except Exception as e:
                    print(e)

        return instance


class ExamDeleteGroupUpdateSerializer(serializers.ModelSerializer):
    group_id = serializers.UUIDField()

    class Meta:
        model = Exam
        fields = ['group_id']

    def update(self, instance, validated_data):
        group_id = validated_data.get('group_id', None)

        if instance.exam_status:
            raise serializers.ValidationError({
                'status': False,
                "message": "Imtihon faolligi sababli guruhni o'chira olmaysiz..."
            })

        if not group_id:
            raise serializers.ValidationError({
                'status': False,
                "message": "Guruh tanlash majburiy..."
            })

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise serializers.ValidationError({
                'status': False,
                "message": "Guruh topilmadi..."
            })
        try:
            ExamStudent.objects.filter(exam=instance, student__group=group).delete()
        except ExamStudent.DoesNotExist:
            pass

        return instance


class ExamStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            'exam_status'
        ]


class ExamStudentForStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamStudent
        fields = ['is_active']

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance


class ExamStudentListSerializer(serializers.ModelSerializer):
    exam = GetExamDetailSerializer()
    is_start = serializers.SerializerMethodField()

    def get_is_start(self, obj):
        try:
            result = Result.objects.get(student=obj.student, exam=obj.exam)
            return result.is_start
        except Result.DoesNotExist:
            return False

    class Meta:
        model = ExamStudent
        fields = ['id', 'exam', 'is_active', 'is_finish', 'is_start']


class ExamListGetSerializer(serializers.ModelSerializer):
    curriculum = GetCurriculumSerializer()
    education_year = GetEducationyearSerializer()
    semester = GetHsemesterSerializer()
    exam_type = ExamTypesSerializer()
    subject = GetSubjectSerializer()
    group_list = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    result_count = serializers.SerializerMethodField()

    def get_question_count(self, obj):
        return obj.exams_question.count()

    def get_result_count(self, obj):
        return obj.exam_results.count()

    def get_group_list(self, obj):
        groups = Group.objects.filter(exam_groups_list__exam=obj).distinct()

        return [
            {
                'id': group.id,
                'name': group.name,
                'faculty': group.faculty.name,
                'educationLang': group.educationLang.name,
                'curriculum': group.group_curriculum.name,
            }
            for group in groups]

    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'comment', 'curriculum', 'education_year',
            'semester', 'exam_type', 'exam_status', 'begin_time',
            'end_time', 'exam_time', 'max_score', 'attempts',
            'total_count', 'is_random', 'subject', 'group_list',
            'question_count', 'result_count',
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'name', 'is_active'
        ]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['name', 'isTrue']


class QuestionSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duplicate_questions_count = 0
        self.new_questions_count = 0

    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['exam', 'name', 'answers', 'is_active']

    def create(self, validated_data):
        question_name = validated_data.get('name')
        exam_id = validated_data.get('exam')
        if Question.objects.filter(name=question_name, exam_id=exam_id).exists():
            self.duplicate_questions_count += 1
        else:
            self.new_questions_count += 1
            answers_data = validated_data.pop('answers', [])
            question = Question.objects.create(**validated_data)
            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return {
            "new_questions_count": self.new_questions_count,
            "duplicate_questions_count": self.duplicate_questions_count
        }


class QuestionUpdateSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['exam', 'name', 'answers', 'is_active']

    def update(self, instance, validated_data):
        instance.exam = validated_data.get('exam', instance.exam)
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        answers_data = validated_data.get('answers', [])
        if not answers_data:
            instance.save()
            return instance
        else:
            instance.answers.all().delete()
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)
            instance.save()

            return instance


class GetAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'name']


class ExamDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name']


class QuestionDetailGetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    exam = ExamDetailSerializer()

    class Meta:
        model = Question
        fields = ['id', 'exam', 'name', 'answers', 'is_active']


class QASerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'name', 'answers']

    def get_answers(self, obj):
        answers = list(obj.answers.all())
        random.shuffle(answers)
        return GetAnswerSerializer(answers, many=True).data


class ResultSerializer(serializers.ModelSerializer):
    percentage = serializers.ReadOnlyField()
    exam_time_second = serializers.ReadOnlyField()
    score = serializers.ReadOnlyField()

    class Meta:
        model = Result
        fields = [
            'exam', 'student', 'group', 'ip_address',
            'attempts', 'total_count', 'max_score', 'begin_time',
            'exam_time', 'exam_time_second', 'percentage', 'score'
        ]


class ResultUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            'ip_address', 'attempts',
            'correct_answer', 'total_count', 'max_score', 'begin_time',
            'end_time', 'is_start', 'exam_time'
        ]


class ResultListSerializer(serializers.ModelSerializer):
    percentage = serializers.ReadOnlyField()
    score = serializers.ReadOnlyField()
    exam_time_second = serializers.ReadOnlyField()
    exam = ExamListGetSerializer()
    student = StudentForResultSerializer()
    group = GetGroupSerializer()

    class Meta:
        model = Result
        fields = [
            'id', 'exam', 'student', 'group', 'ip_address', 'attempts',
            'correct_answer', 'total_count', 'max_score', 'begin_time',
            'end_time', 'is_start', 'exam_time_second', 'percentage',
            'score', 'time_spent'
        ]


class ResultListForGroupSerializer(serializers.ModelSerializer):
    student = StudentForResultSerializer()
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        exam = obj.exam
        student = obj.student

        try:
            if isinstance(student, Student):
                results = Result.objects.filter(exam=exam, student=student)
                if results.exists():
                    result_instance = results.first()
                    return {
                        'attempts': result_instance.attempts,
                        'correct_answer': result_instance.correct_answer,
                        'begin_time': result_instance.begin_time,
                        'end_time': result_instance.end_time,
                        'percentage': result_instance.percentage
                    }
                else:
                    return {
                        'attempts': None,
                        'correct_answer': None,
                        'begin_time': None,
                        'end_time': None,
                        'percentage': None
                    }
            else:
                return {
                    'attempts': None,
                    'correct_answer': None,
                    'begin_time': None,
                    'end_time': None,
                    'percentage': None
                }
        except Result.DoesNotExist:
            return {
                'attempts': None,
                'correct_answer': None,
                'begin_time': None,
                'end_time': None,
                'percentage': None
            }

    class Meta:
        model = ExamStudent
        fields = ['student', 'is_active', 'result']


class QuestionDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class StudentForTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentForTest
        fields = ['exam', 'student', 'json_field']


class StudentExamAnswerSerializer(serializers.ModelSerializer):
    ip_address = serializers.IPAddressField(source='exam.ip_address', read_only=True)

    class Meta:
        model = StudentExamAnswer
        fields = ['question', 'is_selected', 'ip_address']


class StudentExamAnswerFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamAnswer
        fields = ['question', 'is_selected', 'true_answer']


class StudentForTestResultSerializer(serializers.ModelSerializer):
    exam_select_answer = serializers.SerializerMethodField()

    def get_exam_select_answer(self, obj):
        exam_obj = obj.exam
        student_obj = obj.student
        data = StudentExamAnswer.objects.filter(exam=exam_obj, student=student_obj)

        if data.exists():
            serialized_data = StudentExamAnswerFullSerializer(data, many=True).data
            return serialized_data

        return None

    class Meta:
        model = StudentForTest
        fields = ['exam', 'student', 'json_field', 'exam_select_answer']


class SeansSerializer(serializers.Serializer):
    exam_id = serializers.UUIDField()


class QACreateSerializer(serializers.Serializer):
    exam = serializers.UUIDField()
    student = serializers.UUIDField()
    ip_address = serializers.IPAddressField()


class IsLogoutSerializer(serializers.Serializer):
    exam = serializers.UUIDField()
    student = serializers.UUIDField()
