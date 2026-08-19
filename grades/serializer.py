from rest_framework import serializers

from .models import ConnectGrades, Grade

from learning_process.models import Curriculum
from semestr.models import Hsemester
from subjects.models import Subject_Curriculum


class CurriculumGradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'name', 'educationyear', 'educationtype', 'educationform']


class SemesterGradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hsemester
        fields = ['id', 'name']


class Subject_GradesSerializer(serializers.ModelSerializer):
    subject_semestr = SemesterGradesSerializer(many=False)
    subject_curriculum = CurriculumGradesSerializer(many=False)

    class Meta:
        model = Subject_Curriculum
        fields = ['id', 'subject', 'subject_semestr', 'subject_curriculum']


class CreateGradeSerializer(serializers.Serializer):
    subject = serializers.UUIDField()   # Subject_Curriculum.id
    group = serializers.UUIDField()
    students = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False
    )

class ConnectGradeListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.subject.name")
    subjects_id = serializers.UUIDField(source="subject.id")
    curriculum_name = serializers.CharField(source="subject.subject_curriculum.name")
    curriculum_id = serializers.UUIDField(source="subject.subject_curriculum.id")
    semester_name = serializers.CharField(source="subject.subject_semestr.name")
    group_name = serializers.CharField(source="group.name")

    class Meta:
        model = ConnectGrades
        fields = [
            "id",
            "subject_name",
            "curriculum_name",
            "semester_name",
            "group_name",
            "sheet_type",
            "subjects_id",
            "curriculum_id"

        ]

class GradeDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name")

    class Meta:
        model = Grade
        fields = [
            "student_name",
            "jn_score",
            "on_score",
            "yn_score"
        ]

# class CreateGradeSerializer(serializers.Serializer):
#     curriculum = serializers.UUIDField(
#         error_messages={
#             "required": "Majburiy maydon",
#             "invalid": "UUID noto‘g‘ri"
#         }
#     )
#     semester = serializers.UUIDField(
#         error_messages={
#             "required": "Majburiy maydon",
#             "invalid": "UUID noto‘g‘ri"
#         }
#     )
#     group = serializers.UUIDField(
#         error_messages={
#             "required": "Majburiy maydon",
#             "invalid": "UUID noto‘g‘ri"
#         }
#     )
#     subject = serializers.UUIDField(
#         error_messages={
#             "required": "Majburiy maydon",
#             "invalid": "UUID noto‘g‘ri"
#         }
#     )
#
#     students = serializers.ListField(
#         required=True,
#         allow_empty=False,
#         error_messages={
#             "required": "Majburiy maydon",
#             "empty": "Studentlar ro‘yxati bo‘sh bo‘lishi mumkin emas"
#         },
#         child=serializers.UUIDField(
#             error_messages={
#                 "invalid": "Student ID noto‘g‘ri"
#             }
#         )
#     )
#
#     def validate(self, attrs):
#         # None / bo‘sh stringlarni ham bloklaymiz
#         for field in ["curriculum", "semester", "group", "subject"]:
#             if attrs.get(field) in [None, ""]:
#                 raise serializers.ValidationError({
#                     field: "Majburiy maydon"
#                 })
#         return attrs
#
#     def validate_students(self, value):
#         if not value:
#             raise serializers.ValidationError("Studentlar ro‘yxati bo‘sh bo‘lmasligi kerak")
#
#         if len(value) != len(set(value)):
#             raise serializers.ValidationError("Studentlar takrorlangan")
#
#         return value
