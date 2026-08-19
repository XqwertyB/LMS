from rest_framework import serializers
from .models import ExamTypes, EmployeeStatus


class ExamTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamTypes
        fields = ['id', 'name', 'code']


class EmployeeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeStatus
        fields = ['name', 'code']
