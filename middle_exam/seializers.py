from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Middle_exam
from django.utils import timezone

class Middle_exam_list_Serializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()
    is_enabled = serializers.SerializerMethodField()
    class Meta:
        model = Middle_exam
        fields = ['name','exam_status','exam_type',
                  'begin_time','end_time','is_enabled','students_count'
                  ]

    def get_students_count(self,obj):
        try:
            val = obj.middle_exams_student.coun()
        except Exception as ex:
            val = 0
        return val

    def get_is_enabled(self, obj):
        try:
            exam = Middle_exam.objects.get(id=obj.id)
            if exam.begin_time <= timezone.now() <= exam.end_time:
                return True
            else:
                return False
        except exam.DoesNotExist:
            return False