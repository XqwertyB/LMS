from decimal import Decimal

from rest_framework import serializers

from written_exam.another_views.admin_view.serializers import ExamGroupShortSerializer
from written_exam.models import QuestionBank
from written_exam.models import QuestionCollection
from written_exam.models import WrittenExam
from written_exam.models import WrittenExamAnswer
from written_exam.models import WrittenExamAttempt
from written_exam.models import WrittenExamQuestion


class QuestionCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCollection
        fields = ["id", "name"]


class BaseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = [
            "id",
            "collection",
            "text",
            "difficulty",
            "status",
        ]


class TeacherExamListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    curriculum_name = serializers.CharField(source="curriculum.name", read_only=True)
    assigned_groups = ExamGroupShortSerializer(
        source="assigned_exams",
        many=True,
        read_only=True
    )

    class Meta:
        model = WrittenExam
        fields = [
            "id",
            "name",
            "exam_type",
            "subject_name",
            "curriculum_name",
            "begin_time",
            "end_time",
            "max_attempts",
            "max_score",
            "duration_minutes",
            "easy_count",
            "medium_count",
            "hard_count",
            "status",
            "is_editable",
            "assigned_groups",
            "created_at",
        ]


class WrittenExamQuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrittenExamQuestion
        fields = ["id", "text", "difficulty", "status"]


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name")
    group_name = serializers.CharField(source="student.group.name")
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = WrittenExamAttempt
        fields = [
            "id",
            "student",
            "student_name",
            "group_name",
            "attempt_no",
            "status",
            "total_score",
            "started_at",
            "submitted_at"
        ]

    @staticmethod
    def get_total_score(obj):
        return obj.total_score_db or Decimal("0.00")


class StudentAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)

    class Meta:
        model = WrittenExamAnswer
        fields = [
            "question_text",
            "answer_text",
            "score",
        ]


class TeacherAttemptQuestionSerializer(serializers.Serializer):
    question_id = serializers.UUIDField(source="question.id")
    question_text = serializers.CharField(source="question.text")
    answer = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    max_score = serializers.SerializerMethodField()

    def get_answer(self, obj):
        answer = obj.question.answers.filter(attempt=obj.attempt).first()
        return answer.answer_text if answer else None

    def get_score(self, obj):
        answer = obj.question.answers.filter(attempt=obj.attempt).first()
        return answer.score if answer else None

    def get_comment(self, obj):
        answer = obj.question.answers.filter(attempt=obj.attempt).first()
        return answer.comment if answer else None

    def get_max_score(self, obj):
        exam = obj.attempt.exam
        difficulty = obj.question.difficulty

        if difficulty == "easy":
            return exam.easy_total_score / exam.easy_count if exam.easy_count else 0
        elif difficulty == "medium":
            return exam.medium_total_score / exam.medium_count if exam.medium_count else 0
        else:
            return exam.hard_total_score / exam.hard_count if exam.hard_count else 0

class AttemptDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name")
    questions = TeacherAttemptQuestionSerializer(many=True)

    class Meta:
        model = WrittenExamAttempt
        fields = [
            "id",
            "student_name",
            "attempt_no",
            "status",
            "started_at",
            "submitted_at",
            "questions"
        ]


class GradeAnswerSerializer(serializers.Serializer):
    exam_id = serializers.UUIDField()
    student_id = serializers.UUIDField()
    question_id = serializers.UUIDField()
    score = serializers.DecimalField(max_digits=6, decimal_places=2)
    comment = serializers.CharField(required=False,
                                    allow_blank=True,
                                    allow_null=True)


class ExamGroupSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
