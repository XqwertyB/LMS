from rest_framework import serializers, status

from learning_process.serializers import CurriculumSerializer, GetEducationyearSerializer
from .models import HCourse, Hsemester_action, Hsemester, CurriculumWeeks
from rest_framework.exceptions import ValidationError
import re


class HCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HCourse
        fields = '__all__'

    def validate_code(self, value):
        if not re.fullmatch(r'^\d+$', value):
            raise ValidationError("Faqat raqamlardan iboroat bo`lishi kerak !")
        return value

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class HsemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hsemester
        fields = '__all__'

    def validate_code(self, value):
        if not re.fullmatch(r'^\d+$', value):
            raise ValidationError("Faqat raqamlardan iboroat bo`lishi kerak !")
        return value

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class Hsemester_actionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hsemester_action
        fields = '__all__'

    def validate_code(self, value):
        if not re.fullmatch(r'^\d+$', value):
            raise ValidationError("Faqat raqamlardan iboroat bo`lishi kerak !")
        return value

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('h_id'):
            data = {'h_id  ': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class GetHsemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hsemester
        fields = ['id', 'name']


class GetHsemester_actionSerializer(serializers.ModelSerializer):
    semester = GetHsemesterSerializer()
    education_year = GetEducationyearSerializer()

    class Meta:
        model = Hsemester_action
        fields = ['id', 'current', 'semester', 'education_year']
