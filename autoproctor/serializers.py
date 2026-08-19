from rest_framework import serializers

from exam.serializer import ExamDetailSerializer
from students.serializers import StudentForResultSerializer
from .models import ScreenModel


class ScreenModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenModel
        fields = ['student', 'exam', 'image']

    def validate(self, data):
        student = data.get('student', None)
        exam = data.get('exam', None)
        image = data.get('image', None)

        if student is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Talaba yuborilmayapti..."
                }
            )

        if exam is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Imtihon yuborilmayapti..."
                }
            )

        if image is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Hech qanday fayl yuborilmadi..."
                }
            )
        return data


class ScreenDetailSerializer(serializers.ModelSerializer):
    exam = ExamDetailSerializer()
    student = StudentForResultSerializer()

    class Meta:
        model = ScreenModel
        fields = ['id', 'student', 'exam', 'image', 'attempts', 'is_active']


class ScreenListSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    exam = serializers.SerializerMethodField()

    def get_student(self, obj):
        return {
            "id": obj.student.id,
            "full_name": obj.student.full_name
        }

    def get_exam(self, obj):
        return {
            "id": obj.exam.id,
            "name": obj.exam.name
        }

    class Meta:
        model = ScreenModel
        fields = ('student', 'exam', 'attempts', 'is_active')
