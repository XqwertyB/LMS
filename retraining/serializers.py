from rest_framework import serializers
from django.utils import timezone
from students.models import Student
from students.serializers import StudentSerializer
from user.models import User
from learning_process.models import Educationlang
from .models import (
    ReTrainingGroup, ReTrainingStudent, Assignment,
    TestQuestion, TestQuestionOption, AssignmentSubmission, TestAnswer
)
from .test_parser import parse_test_text


class RetrainingTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class EducationLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationlang
        fields = ['id', 'name']


class ReTrainingGroupBasicSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = ReTrainingGroup
        fields = [
            'id', 'name', 'description', 'max_students', 'min_students',
            'teacher', 'teacher_name', 'language',
            'start_date', 'end_date', 'registration_start', 'registration_end',
            'created_at', 'is_active'
        ]

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала.")
        return data


class StudentBasicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    student_id_number = serializers.CharField()


# class StudentBasicSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     full_name = serializers.CharField()
#     student_id_number = serializers.CharField()
#     email = serializers.EmailField(allow_null=True)
#     phone = serializers.CharField(allow_null=True)
#     specialty = serializers.SerializerMethodField()
#     group = serializers.SerializerMethodField()
#
#     def get_specialty(self, obj):
#         return {
#             'id': obj.specialty.id,
#             'name': getattr(obj.specialty, 'name', str(obj.specialty))
#         } if obj.specialty else None
#
#     def get_group(self, obj):
#         return {
#             'id': obj.group.id,
#             'name': getattr(obj.group, 'name', str(obj.group))
#         } if obj.group else None


class ReTrainingStudentBasicSerializer(serializers.ModelSerializer):
    student_details = StudentBasicSerializer(source='student', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = ReTrainingStudent
        fields = ['id', 'student', 'student_details', 'group', 'group_name', 'status', 'enrolled_at']


class ReTrainingStudentSerializer(serializers.ModelSerializer):
    student_details = StudentBasicSerializer(source='student', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    enrolled_by_name = serializers.CharField(source='enrolled_by.get_full_name', read_only=True)

    class Meta:
        model = ReTrainingStudent
        fields = [
            'id', 'student', 'student_details', 'group', 'group_name',
            'status', 'notes', 'enrolled_by', 'enrolled_by_name', 'enrolled_at', 'is_active'
        ]


class ReTrainingStudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReTrainingStudent
        fields = ['student', 'group', 'notes']

    def validate(self, data):
        student = data['student']
        group = data['group']
        if ReTrainingStudent.objects.filter(student=student, group=group, is_active=True).exists():
            raise serializers.ValidationError("Студент уже зарегистрирован в этой группе.")

        today = timezone.now().date()
        if group.registration_start and today < group.registration_start:
            raise serializers.ValidationError("Регистрация ещё не началась.")
        if group.registration_end and today > group.registration_end:
            raise serializers.ValidationError("Регистрация завершена.")

        if group.retraining_students.filter(is_active=True).count() >= group.max_students:
            raise serializers.ValidationError("Превышен лимит студентов в группе.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['enrolled_by'] = request.user
        return super().create(validated_data)


class BulkStudentAddSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(queryset=ReTrainingGroup.objects.all())
    student_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        group = data['group']
        student_ids = data['student_ids']

        existing_students = Student.objects.filter(id__in=student_ids)
        if existing_students.count() != len(student_ids):
            raise serializers.ValidationError("Один или несколько студентов не найдены.")

        if group.retraining_students.filter(is_active=True).count() + len(student_ids) > group.max_students:
            raise serializers.ValidationError("Превышен лимит студентов в группе.")

        return data


class ReTrainingGroupWithStudentsSerializer(serializers.ModelSerializer):
    teacher_details = RetrainingTeacherSerializer(source='teacher', read_only=True)
    language_details = EducationLanguageSerializer(source='language', read_only=True)
    students = serializers.SerializerMethodField()

    class Meta:
        model = ReTrainingGroup
        fields = [
            'id', 'name', 'description', 'teacher', 'teacher_details',
            'language', 'language_details', 'faculty', 'speciality',
            'start_date', 'end_date', 'registration_start', 'registration_end',
            'min_students', 'max_students', 'students', 'created_at'
        ]

    def get_students(self, obj):
        students = obj.retraining_students.filter(is_active=True)
        return ReTrainingStudentBasicSerializer(students, many=True).data


####################################################################################

class TestQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQuestionOption
        fields = ['id', 'option_text', 'is_correct', 'order']


class TestQuestionSerializer(serializers.ModelSerializer):
    options = TestQuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = TestQuestion
        fields = [
            'id', 'assignment', 'question_text', 'question_type',
            'order', 'points', 'correct_answer',
            'is_required', 'is_active', 'options'
        ]


class TestQuestionOptionStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQuestionOption
        fields = ['id', 'option_text', 'order']  # ⚠️ без is_correct


class TestQuestionStudentSerializer(serializers.ModelSerializer):
    options = TestQuestionOptionStudentSerializer(many=True, read_only=True)

    class Meta:
        model = TestQuestion
        fields = [
            'id', 'assignment', 'question_text', 'question_type',
            'order', 'points', 'is_required', 'is_active', 'options'
        ]


class TestQuestionOptionTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQuestionOption
        fields = ['id', 'option_text', 'is_correct', 'order']


class TestQuestionTeacherSerializer(serializers.ModelSerializer):
    options = TestQuestionOptionTeacherSerializer(many=True, read_only=True)

    class Meta:
        model = TestQuestion
        fields = [
            'id', 'assignment', 'question_text', 'question_type',
            'order', 'points', 'correct_answer',
            'is_required', 'is_active', 'options'
        ]


class AssignmentSerializer(serializers.ModelSerializer):
    questions = TestQuestionSerializer(many=True, read_only=True)
    submissions_count = serializers.IntegerField(read_only=True)
    completed_submissions_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'

    def validate(self, data):
        # Для существующего объекта при обновлении

        request = self.context.get('request')
        if request and request.method == 'PATCH':
            status = request.query_params.get('status')
            if status:
                data['status'] = status

        if self.instance:
            # Берем новые значения или существующие
            start_datetime = data.get('start_datetime', self.instance.start_datetime)
            end_datetime = data.get('end_datetime', self.instance.end_datetime)
        else:
            # Для нового объекта
            start_datetime = data.get('start_datetime')
            end_datetime = data.get('end_datetime')

        # Проверяем только если обе даты доступны
        if start_datetime and end_datetime:
            if start_datetime >= end_datetime:
                raise serializers.ValidationError({
                    'end_datetime': 'Дата окончания должна быть позже даты начала.'
                })

            # Дополнительная проверка минимальной длительности
            duration = end_datetime - start_datetime
            if duration.total_seconds() < 300:  # 5 минут
                raise serializers.ValidationError({
                    'end_datetime': 'Минимальная длительность задания - 5 минут.'
                })

        return data


class AssignmentSerializerForStudent(AssignmentSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        for question in data.get('questions', []):
            question.pop('correct_answer', None)
            for opt in question.get('options', []):
                opt.pop('is_correct', None)
        return data


class ReTrainingStudentBasicSerializer(serializers.ModelSerializer):
    # Сериализатор для модели ReTrainingStudent
    student_details = StudentBasicSerializer(source='student', read_only=True)

    class Meta:
        model = ReTrainingStudent
        fields = ['id', 'student', 'student_details', 'status', 'enrolled_at', 'is_active']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student = ReTrainingStudentBasicSerializer(read_only=True)
    percentage_score = serializers.FloatField(read_only=True)
    is_passed = serializers.BooleanField(read_only=True)
    time_taken = serializers.DurationField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'student', 'status', 'attempt_number',
            'started_at', 'completed_at', 'graded_at',
            'score', 'max_score', 'grade',
            'submission_file', 'student_comment', 'teacher_comment',
            'graded_by', 'ip_address', 'test_data',
            'percentage_score', 'is_passed', 'time_taken', 'is_overdue'
        ]
        read_only_fields = ['started_at', 'graded_at', 'score', 'grade', 'max_score', 'graded_by']

    def create(self, validated_data):
        assignment = validated_data.get('assignment')
        validated_data['max_score'] = assignment.question_count  # грубая оценка: 1 балл за вопрос
        return super().create(validated_data)


class TestAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAnswer
        fields = [
            'id', 'submission', 'question',
            'selected_options', 'text_answer',
            'is_correct', 'points_earned'
        ]
        read_only_fields = ['is_correct', 'points_earned']

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.check_answer()
        return instance


class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'group', 'assignment_type',
            'start_datetime', 'end_datetime', 'max_attempts',
            'duration_minutes', 'is_published'
        ]

    def validate(self, data):
        start = data.get('start_datetime')
        end = data.get('end_datetime')
        if start and end and end <= start:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class GradeSubmissionSerializer(serializers.Serializer):
    grade = serializers.FloatField(min_value=0, max_value=100)
    teacher_comment = serializers.CharField(required=False, allow_blank=True)


class SubmissionDetailSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    student = ReTrainingStudentBasicSerializer(read_only=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'student',
            'status', 'attempt_number',
            'started_at', 'completed_at', 'graded_at',
            'score', 'max_score', 'grade',
            'submission_file', 'student_comment', 'teacher_comment',
            'graded_by', 'ip_address', 'test_data',
            'answers'
        ]

    def get_answers(self, obj):
        answers = TestAnswer.objects.filter(submission=obj).select_related('question')
        return TestAnswerSerializer(answers, many=True).data


class ReTrainingGroupSerializer(serializers.ModelSerializer):
    meeting_id = serializers.CharField(source='online_room.meetingID', read_only=True)
    join_url = serializers.SerializerMethodField()

    class Meta:
        model = ReTrainingGroup
        fields = [..., 'meeting_id', 'join_url']

    def get_join_url(self, obj):
        if obj.online_room:
            return f"{obj.online_room.logoutURL}?meetingID={obj.online_room.meetingID}"
        return None


class TestQuestionRetrieveSerializer(serializers.ModelSerializer):
    options = TestQuestionOptionSerializer(many=True, read_only=True)  # Вложенный список ответов

    class Meta:
        model = TestQuestion
        fields = ('id', 'question_text', 'question_type', 'options')


class TestQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQuestionOption
        fields = ('id', 'question', 'question_text', 'is_correct')  # Вывод is_correct может быть ограничен для учеников


class TextTestCreateSerializer(serializers.Serializer):
    text = serializers.JSONField()  # Универсальный формат (str yoki list)
    assignment = serializers.CharField()

    def validate_assignment(self, value):
        try:
            return Assignment.objects.get(id=value)
        except Assignment.DoesNotExist:
            raise serializers.ValidationError("Assignment topilmadi.")

    def create(self, validated_data):
        assignment = validated_data["assignment"]
        raw_text = validated_data["text"]

        # 🔥 Универсальная обработка формата (строка или список)
        if isinstance(raw_text, str):
            raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
            text_list = [q.strip() for q in raw_text.split("++++") if q.strip()]
        elif isinstance(raw_text, list):
            text_list = [
                t.replace("\r\n", "\n").replace("\r", "\n")
                for t in raw_text if t.strip()
            ]
        else:
            raise serializers.ValidationError("text noto'g'ri formatda (str yoki list bo'lishi kerak)")

        if not text_list:
            raise serializers.ValidationError("Hech qanday savol topilmadi")

        # 🔥 Универсальный парсер → сразу массив вопросов
        questions = parse_test_text(text_list)

        if not questions:
            raise serializers.ValidationError("Test savollarini yechib bo'lmadi. Formatni tekshiring!")

        # 🧠 Создаём вопросы в БД
        for q in questions:
            options = q.pop("options")
            question_obj = TestQuestion.objects.create(
                assignment=assignment,
                **q
            )
            for opt in options:
                TestQuestionOption.objects.create(
                    question=question_obj,
                    **opt
                )

        assignment.question_count = assignment.questions.count()
        assignment.save(update_fields=["question_count"])

        return assignment
