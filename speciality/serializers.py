from rest_framework import serializers, status
from .models import Bspeciality, Mspeciality, Ospeciality,AllSpeciality
from rest_framework.exceptions import ValidationError
import re


class BspecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bspeciality
        ref_name = 'SpecialityBspeciality'
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


class MspecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Mspeciality
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


class OspecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ospeciality
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

class AllSpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AllSpeciality
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