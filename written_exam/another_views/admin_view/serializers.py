from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from learning_process.models import Curriculum
from subjects.models import Subject
from user.models import User
from written_exam.models import WrittenExam, WrittenExamQuestion
from written_exam.models import WrittenExamGroup

from django.core.exceptions import ValidationError as DjangoValidationError

class WrittenExamCreateSerializer(serializers.ModelSerializer):
    """
    Imtihon yaratish serializeri
    """

    curriculum = serializers.PrimaryKeyRelatedField(
        queryset=Curriculum.objects.all(),
        error_messages={"message": "O‘quv reja topilmadi"}
    )

    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        error_messages={"message": "Fan topilmadi"}
    )

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher', is_active=True),
        error_messages={"message": "O‘qituvchi topilmadi"}
    )

    grader = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher', is_active=True),
        error_messages={"message": "Tekshiruvchi o‘qituvchi topilmadi"}
    )

    class Meta:
        model = WrittenExam
        fields = [
            'id',
            'name',
            'description',
            'exam_type',
            'curriculum',
            'subject',
            'teacher',
            'grader',
            'begin_time',
            'end_time',
            'duration_minutes',
            'max_attempts',
            'max_score',
            'easy_count',
            'medium_count',
            'hard_count',
            'shuffle_questions',
            'easy_total_score',
            'medium_total_score',
            'hard_total_score',
        ]

    def validate(self, data):
        now_time = timezone.now()

        begin = data['begin_time']
        end = data['end_time']

        # vaqt tartibi
        if begin >= end:
            raise serializers.ValidationError(
                {"message":"Boshlanish vaqti tugash vaqtidan oldin bo‘lishi kerak"}
            )

        # o‘tmishda boshlanishni bloklash (1 min tolerantlik)
        if begin < now_time - timedelta(minutes=1):
            raise serializers.ValidationError(
                {"message":"Boshlanish vaqti hozirgi vaqtdan kichik bo‘lmasligi kerak" }
            )

        # duration oynaga sig‘ishi kerak
        window = end - begin
        if window < timedelta(minutes=data['duration_minutes']):
            raise serializers.ValidationError(
                {"message":"Imtihon davomiyligi umumiy vaqt oralig‘idan katta bo‘lishi mumkin emas"}
            )

        # savollar soni
        easy = data['easy_count']
        medium = data['medium_count']
        hard = data['hard_count']

        if any(v < 0 for v in (easy, medium, hard)):
            raise serializers.ValidationError(
                {"message":"Savollar soni manfiy bo‘lishi mumkin emas" }
            )

        total = easy + medium + hard
        if total == 0:
            raise serializers.ValidationError(
                {"message":"Kamida bitta savol bo‘lishi kerak"}
            )

        # duration
        if data['duration_minutes'] <= 0:
            raise serializers.ValidationError(
                {"message":"Imtihon davomiyligi noto‘g‘ri kiritildi"}
            )

        # attempts
        if data['max_attempts'] <= 0:
            raise serializers.ValidationError(
                {"message": "Urinishlar soni noto‘g‘ri kiritildi"}
            )

        # score
        if data['max_score'] <= 0:
            raise serializers.ValidationError(
                {"message":"Maksimal ball noto‘g‘ri kiritildi"}
            )

        return data

    def create(self, validated_data):
        request_user = self.context['request'].user

        instance = WrittenExam(
            created_by=request_user,
            **validated_data
        )

        try:
            # 🔥 AVVAL VALIDATE
            instance.full_clean()

        except DjangoValidationError as e:

            if hasattr(e, "message_dict"):
                errors = e.message_dict.get("__all__", [])

                for key, val in e.message_dict.items():
                    if key != "__all__":
                        errors.extend(val)

                raise serializers.ValidationError({
                    "message": errors
                })

            raise serializers.ValidationError({
                "message": e.messages
            })

        # 🔥 KEYIN SAVE
        instance.save()
        return instance



class WrittenExamStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrittenExam
        fields = ['status']


class BaseWrittenExamUpdateSerializer(serializers.ModelSerializer):

    curriculum = serializers.PrimaryKeyRelatedField(
        queryset=Curriculum.objects.all(),
        error_messages={"message": "O‘quv reja topilmadi"}
    )

    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        error_messages={"message": "Fan topilmadi"}
    )

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher', is_active=True),
        error_messages={"message": "O‘qituvchi topilmadi"}
    )

    grader = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher', is_active=True),
        error_messages={"message": "Tekshiruvchi o‘qituvchi topilmadi"}
    )

    class Meta:
        model = WrittenExam
        fields = [
            'id',
            'name',
            'description',
            'exam_type',
            'curriculum',
            'subject',
            'teacher',
            'grader',
            'begin_time',
            'end_time',
            'duration_minutes',
            'max_attempts',
            'max_score',
            'easy_count',
            'medium_count',
            'hard_count',
            'shuffle_questions',
            'easy_total_score',
            'medium_total_score',
            'hard_total_score',
        ]

    # =========================
    # 🔥 FIXED VALIDATE
    # =========================
    def validate(self, data):
        instance = self.instance
        now = timezone.now()

        # 🔥 MERGE (PATCH safe)
        begin = data.get("begin_time", instance.begin_time)
        end = data.get("end_time", instance.end_time)
        duration = data.get("duration_minutes", instance.duration_minutes)

        easy = data.get("easy_count", instance.easy_count)
        medium = data.get("medium_count", instance.medium_count)
        hard = data.get("hard_count", instance.hard_count)

        max_attempts = data.get("max_attempts", instance.max_attempts)
        max_score = data.get("max_score", instance.max_score)

        # vaqt tartibi
        if begin >= end:
            raise serializers.ValidationError({"message": "Boshlanish vaqti tugash vaqtidan oldin bo‘lishi kerak"})

        if begin < now - timedelta(minutes=1):
            raise serializers.ValidationError({"message": "Boshlanish vaqti hozirgi vaqtdan kichik bo‘lmasligi kerak"})

        window = end - begin
        if window < timedelta(minutes=duration):
            raise serializers.ValidationError({"message": "Imtihon davomiyligi umumiy vaqt oralig‘idan katta bo‘lishi mumkin emas"})

        # savollar
        if any(v < 0 for v in (easy, medium, hard)):
            raise serializers.ValidationError({"message": "Savollar soni manfiy bo‘lishi mumkin emas"})

        if (easy + medium + hard) == 0:
            raise serializers.ValidationError({"message": "Kamida bitta savol bo‘lishi kerak"})

        # duration
        if duration <= 0:
            raise serializers.ValidationError({"message": "Imtihon davomiyligi noto‘g‘ri kiritildi"})

        # attempts
        if max_attempts <= 0:
            raise serializers.ValidationError({"message": "Urinishlar soni noto‘g‘ri kiritildi"})

        # score
        if max_score <= 0:
            raise serializers.ValidationError({"message": "Maksimal ball noto‘g‘ri kiritildi"})

        return data

    # =========================
    # 🔥 FULL CLEAN (MUHIM)
    # =========================
    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean()

        except DjangoValidationError as e:

            if hasattr(e, "message_dict"):
                errors = e.message_dict.get("__all__", [])

                # boshqa field errorlarni ham qo‘shib yuboramiz
                for key, val in e.message_dict.items():
                    if key != "__all__":
                        errors.extend(val)

                raise serializers.ValidationError({
                    "message": errors
                })

            raise serializers.ValidationError({
                "message": e.messages
            })

        instance.save()
        return instance


class WrittenExamListSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.employee.full_name", read_only=True)
    grader_name = serializers.CharField(source="grader.employee.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    curriculum_name = serializers.CharField(source="curriculum.name", read_only=True)

    class Meta:
        model = WrittenExam
        fields = [
            'id',

            'name',
            'description',

            'exam_type',

            'curriculum_name',
            'subject_name',
            'teacher_name',
            'grader_name',

            'begin_time',
            'end_time',

            'duration_minutes',

            'max_attempts',
            'max_score',

            'easy_count',
            'medium_count',
            'hard_count',

            'shuffle_questions',

            'status',
        ]


class ExamGroupShortSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="group.id")
    name = serializers.CharField(source="group.name")

    class Meta:
        model = WrittenExamGroup
        fields = ["id", "name"]


class WrittenExamDetailSerializer(serializers.ModelSerializer):
    assigned_groups = ExamGroupShortSerializer(
        source="assigned_exams",
        many=True,
        read_only=True
    )

    class Meta:
        model = WrittenExam
        fields = [
            'id',

            'name',
            'description',

            'exam_type',

            'curriculum',
            'subject',
            'teacher',
            'grader',

            'begin_time',
            'end_time',

            'duration_minutes',

            'max_attempts',
            'max_score',

            'easy_count',
            'medium_count',
            'hard_count',

            'shuffle_questions',

            'status',

            'assigned_groups',
            'easy_total_score',
            'medium_total_score',
            'hard_total_score',
        ]


class WrittenExamQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WrittenExamQuestion
        fields = [
            "id",
            "text",
            "status",

        ]