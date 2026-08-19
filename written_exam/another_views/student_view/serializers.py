from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from written_exam.models import AttemptQuestion, WrittenExamQuestion
from written_exam.models import WrittenExam, WrittenExamAttempt
from written_exam.models import WrittenExamAnswer


class MyWrittenExamGetSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    total_score = serializers.SerializerMethodField()
    is_finished = serializers.SerializerMethodField()
    attempt_count = serializers.SerializerMethodField()
    remaining_attempts = serializers.SerializerMethodField()
    exam_status = serializers.SerializerMethodField()

    class Meta:
        model = WrittenExam
        fields = [
            "id",
            "name",
            "description",
            "subject_name",
            "teacher_name",
            "begin_time",
            "end_time",
            "duration_minutes",
            "max_score",
            "status",
            "total_questions",
            "easy_count",
            "medium_count",
            "hard_count",
            "exam_status",
            "attempt_count",
            "remaining_attempts",
            "is_finished",
            "total_score",
        ]

    def get_attempt_queryset(self, obj):
        student = getattr(self.context["request"].user, "student", None)
        if not student:
            return WrittenExamAttempt.objects.none()

        return WrittenExamAttempt.objects.filter(
            exam=obj,
            student=student
        )

    def get_attempt_count(self, obj):
        return self.get_attempt_queryset(obj).count()

    def get_remaining_attempts(self, obj):
        attempts = self.get_attempt_queryset(obj).count()
        return max(obj.max_attempts - attempts, 0)

    def get_is_finished(self, obj):
        attempts = self.get_attempt_queryset(obj)
        return attempts.filter(status="submitted").exists()

    def get_total_score(self, obj):
        attempts = self.get_attempt_queryset(obj)
        last_attempt = attempts.order_by("-attempt_no").first()
        if not last_attempt:
            return 0

        return (
                last_attempt.answers.aggregate(total=Sum("score"))["total"]
                or 0
        )

    def get_exam_status(self, obj):
        now = timezone.now()
        if now < obj.begin_time:
            return "upcoming"
        if obj.begin_time <= now <= obj.end_time:
            return "active"
        return "finished"


class WrittenExamAnswerUpdateSerializer(serializers.Serializer):
    attempt_question_id = serializers.IntegerField()
    answer_text = serializers.CharField()

    def validate(self, attrs):
        user = self.context["request"].user
        attempt_question_id = attrs["attempt_question_id"]

        try:
            attempt_question = AttemptQuestion.objects.select_related(
                "attempt"
            ).get(
                pk=attempt_question_id,
                attempt__student__user=user
            )
        except AttemptQuestion.DoesNotExist:
            raise serializers.ValidationError("Sizga tegishli bo‘lmagan savol")

        if attempt_question.attempt.submitted_at:
            raise serializers.ValidationError("Imtihon allaqachon yakunlangan")

        attrs["attempt_question"] = attempt_question
        return attrs

    def save(self, **kwargs):
        attempt_question = self.validated_data["attempt_question"]

        answer, _ = WrittenExamAnswer.objects.get_or_create(
            attempt=attempt_question.attempt,
            question=attempt_question.question
        )

        answer.answer_text = self.validated_data["answer_text"]
        answer.save(update_fields=["answer_text"])

        return answer


class WrittenExamFinishSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()

    def validate(self, attrs):
        user = self.context["request"].user
        attempt_id = attrs["attempt_id"]

        try:
            attempt = WrittenExamAttempt.objects.get(
                pk=attempt_id,
                student__user=user
            )
        except WrittenExamAttempt.DoesNotExist:
            raise serializers.ValidationError("Attempt topilmadi")

        if attempt.submitted_at:
            raise serializers.ValidationError("Allaqachon yakunlangan")

        attrs["attempt"] = attempt
        return attrs

    def save(self, **kwargs):
        attempt = self.validated_data["attempt"]
        attempt.submitted_at = timezone.now()
        attempt.status = "submitted"
        attempt.save(update_fields=["submitted_at", "status"])
        return attempt


class WrittenExamAnswerDetailSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)
    exam_id = serializers.IntegerField(source="attempt.exam.id", read_only=True)

    class Meta:
        model = WrittenExamAnswer
        fields = [
            "id",
            "exam_id",
            "question_text",
            "answer_text",
            "score",
        ]


class StudentWrittenExamDetailSerializer(serializers.ModelSerializer):
    exam_name = serializers.CharField(source="exam.name", read_only=True)
    subject_name = serializers.CharField(source="exam.subject.name", read_only=True)
    answers = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = WrittenExamAttempt
        fields = [
            "id",
            "exam_name",
            "subject_name",
            "status",
            "total_score",
            "answers",
        ]

    def get_total_score(self, obj):
        return obj.answers.aggregate(total=Sum("score"))["total"] or 0

    def get_answers(self, obj):
        answers = obj.answers.select_related("question")
        return [
            {
                "question": a.question.text,
                "answer_text": a.answer_text,
                "score": a.score,
                "is_checked": a.is_checked,
            }
            for a in answers
        ]


class StudentWrittenExamSerializerList(serializers.ModelSerializer):
    exam_type = serializers.CharField(source="get_exam_type_display")
    exam_state = serializers.SerializerMethodField()
    attempts_left = serializers.SerializerMethodField()

    class Meta:
        model = WrittenExam
        fields = [
            "id",
            "name",
            "exam_type",
            "begin_time",
            "end_time",
            "duration_minutes",
            "max_score",
            "total_questions",
            "max_attempts",
            "attempts_left",
            "exam_state",
        ]

    def get_attempts_left(self, obj):
        return max(obj.max_attempts - obj.attempt_count, 0)

    def get_exam_state(self, obj):
        student = self.context["student"]
        now = timezone.now()

        if obj.is_blocked:
            return "blocked"

        attempts = obj.student_attempts

        active = None
        for a in attempts:
            if a.status == "in_progress":
                active = a
                break

        if active:

            if now > active.expires_at:
                return "expired"

            session = getattr(active, "session", None)

            if not session:
                return "terminated"

            if session.locked:
                return "terminated"

            delta = now - session.last_activity

            if delta.total_seconds() > obj.inactivity_timeout_minutes * 60:
                return "terminated"

            return "in_progress"

        if obj.attempt_count >= obj.max_attempts:
            return "no_attempts_left"

        return "not_started"


class AttemptQuestionSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text')
    answer = serializers.SerializerMethodField()

    def get_answer(self, obj):
        answer = obj.attempt.answers.filter(question=obj.question).first()
        return answer.answer_text if answer else ""

    class Meta:
        model = AttemptQuestion
        fields = ['id', 'order', 'question_text', 'answer']


class GetAnswerSerializer(serializers.Serializer):
    question_id = serializers.UUIDField(required=True)
    answer = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )


class FinishExamSerializer(serializers.Serializer):
    exam_id = serializers.UUIDField(required=True)


class StudentExamResultSerializer(serializers.Serializer):
    exam_id = serializers.UUIDField()
    attempt_no = serializers.IntegerField()
    status = serializers.CharField()

    total_questions = serializers.IntegerField()
    graded_answers = serializers.IntegerField()
    ungraded_answers = serializers.IntegerField()

    total_score = serializers.DecimalField(
        max_digits=6,
        decimal_places=2
    )
