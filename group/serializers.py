from rest_framework import serializers, status
from .models import Group
from rest_framework.exceptions import ValidationError
import re
from learning_process.serializers import EducationlangSerializer, CurriculumSerializer
from universty.serializers import FacultySerializer
from speciality.serializers import BspecialitySerializer, AllSpecialitySerializer


class GroupSerializer(serializers.ModelSerializer):
    educationLang = EducationlangSerializer(read_only=True, many=False)
    faculty = FacultySerializer(read_only=True)
    specialty = serializers.SerializerMethodField()  # override qilyapmiz
    group_curriculum = CurriculumSerializer(many=False)

    class Meta:
        model = Group
        fields = '__all__'

    def get_specialty(self, obj):
        # Agar new_specialty mavjud bo‘lsa, uni serialize qilamiz
        if obj.new_specialty:
            return AllSpecialitySerializer(obj.new_specialty).data
        # Aks holda eski specialty chiqadi
        elif obj.specialty:
            return BspecialitySerializer(obj.specialty).data
        return None

    def validate_h_id(self, value):
        if not re.fullmatch(r'^\d+$', str(value)):
            raise ValidationError("Faqat raqamlardan iborat bo‘lishi kerak !")
        return value

    def validate(self, attrs):
        if not attrs.get('name'):
            raise ValidationError({'name': "Bo‘sh qiymat!"})
        elif not attrs.get('h_id'):
            raise ValidationError({'h_id': "Bo‘sh qiymat!"})
        elif not attrs.get('faculty'):
            raise ValidationError({'faculty': "Bo‘sh qiymat!"})
        elif not attrs.get('educationLang'):
            raise ValidationError({'educationLang': "Bo‘sh qiymat!"})
        elif not attrs.get('group_curriculum'):
            raise ValidationError({'group_curriculum': "Bo‘sh qiymat!"})
        return attrs


class ListGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'educationLang']


class GetGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class GroupViewSerializer(serializers.ModelSerializer):
    educationLang = EducationlangSerializer(read_only=True, many=False)
    faculty = FacultySerializer(many=False, read_only=True)
    specialty = serializers.SerializerMethodField()  # override qilyapmiz
    group_curriculum = CurriculumSerializer(read_only=True, many=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'group_curriculum', 'faculty', 'specialty', 'educationLang']

    def get_specialty(self, obj):
        # Agar new_specialty mavjud bo‘lsa, uni serialize qilamiz
        if obj.new_specialty:
            return AllSpecialitySerializer(obj.new_specialty).data
        # Aks holda eski specialty chiqadi
        elif obj.specialty:
            return BspecialitySerializer(obj.specialty).data
        return None
