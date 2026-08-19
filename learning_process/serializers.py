from django.db.models import Q
from rest_framework import serializers, status

from mixcontent.models import ConnectSpeciality
from semestr.models import Hsemester_action
from universty.serializers import FacultySerializer
from .models import Educationyear, Educationtype, Educationform, MarkingSystem, Curriculum, Science_branch, \
    Educationlang
from rest_framework.exceptions import ValidationError
import re
from speciality.serializers import BspecialitySerializer
from content.models import Content


class EducationyearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationyear
        fields = '__all__'

    def validate_code(self, value):
        try:
            x = value.split('-')
            if not re.fullmatch(r'^\d+$', x[0]):
                raise ValidationError("Faqat raqamlardan iboroat bo`lishi kerak !")
            if not re.fullmatch(r'^\d+$', x[1]):
                raise ValidationError("Faqat raqamlardan iboroat bo`lishi kerak !")
        except:
            raise ValidationError("Qiymat noto`g'ri kirtilgan !")
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


class EducationtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationtype
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


class EducationformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationform
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


class MarkingSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkingSystem
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
        elif not attrs.get('minimum_limit'):
            data = {'minimum_limit': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('gpa_limit'):
            data = {'gpa_limit': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class CurriculumSerializer(serializers.ModelSerializer):
    educationyear = EducationyearSerializer(read_only=True, many=False)
    educationtype = EducationtypeSerializer(read_only=True, many=False)
    educationform = EducationformSerializer(read_only=True, many=False)
    markingsystem = MarkingSystemSerializer(read_only=True, many=False)
    department = FacultySerializer()
    smester = serializers.SerializerMethodField()

    class Meta:
        model = Curriculum
        fields = ['id', 'cur_id', 'name', 'specialty','new_specialty', 'educationyear', 'educationtype', 'educationform',
                  'markingsystem', 'semester_count', 'education_period', 'department', 'smester', 'status_action']

    def get_smester(self, obj):
        result = Hsemester_action.objects.filter(Q(curriculum=obj.id), Q(current=True)).first()
        if result:
            return {
                'id': result.semester.id,
                'name': result.semester.name
            }
        else:
            return None

    def validate_code(self, value):
        if not re.fullmatch(r'^\d+$', value):
            raise ValidationError("Faqat raqamlardan iboroat bo`lishi kerak !")
        return value

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('cur_id'):
            data = {'cur_id': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('semester_count'):
            data = {'semester_count': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('education_period'):
            data = {'education_period': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class Science_branchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Science_branch
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class EducationlangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationlang
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


class GetCurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'name']


class GetEducationyearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationyear
        fields = ['id', 'name', 'code', 'current']


class GetCurriculumOneSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    class Meta:
        model = Content
        fields = ['name','subject']
    def get_name(self,obj):
        try:
            return obj.curriculum_id.name
        except Exception as ex:
            return None

    def get_subject(self, obj):
        try:
            return obj.subject_id.name
        except Exception as ex:
            return None