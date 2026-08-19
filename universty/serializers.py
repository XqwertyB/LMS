import re

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from .models import Otmtype, Otmshape, Otm, Faculty_type, Faculty, Department, Section, City, OtmSection


class OtmtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otmtype
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


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('parent'):
            data = {'parent': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class OtmshapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otmshape
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


class OtmSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=False)
    ownership = OtmtypeSerializer(many=False)
    universityForm = OtmshapeSerializer(many=False)

    class Meta:
        model = Otm
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('kod'):
            data = {'kod': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('area_located'):
            data = {'area_located': "Bo`sh qiymat!"}
            raise ValidationError(data)
        # elif not attrs.get('city'):
        #     data = {'soato': "Bo`sh qiymat!"}
        #     raise ValidationError(data)
        elif not attrs.get('phone'):
            data = {'phone': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('stir'):
            data = {'stir': "Bo`sh qiymat!"}
            raise ValidationError(data)
        # elif not attrs.get('rektor'):
        #     data = {'rektor': "Bo`sh qiymat!"}
        #     raise ValidationError(data)
        # elif not attrs.get('ownership'):
        #     data = {'ownership': "Bo`sh qiymat!"}
        #     raise ValidationError(data)
        # elif not attrs.get('universityForm'):
        #     data = {'universityForm': "Bo`sh qiymat!"}
        #     raise ValidationError(data)
        elif not attrs.get('address'):
            data = {'address': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('bank_info'):
            data = {'bank_info': "Bo`sh qiymat!"}
            raise ValidationError(data)
        # elif not attrs.get('akkreditasiya_info'):
        #     data = {'akkreditasiya_info': "Bo`sh qiymat!"}
        #     raise ValidationError(data)
        else:
            return attrs

    def validate_phone(self, phone):
        phone_regex = re.compile(r"^\+998[35789]\d{8}$")
        if re.fullmatch(phone_regex, phone):
            return phone
        else:
            data = {
                "status": False,
                'message': "Contact nomeri to'g'ri kiritilmadi!"
            }
            raise ValidationError(data)

    def validate_stir(self, stir):
        if stir.isdigit() and len(stir) >= 9:
            return stir
        else:
            data = {
                "status": False,
                'message': "STIR noto'g'ri kiritildi, kamida 9 ta raqamdan iborat bo'lishi shart!"
            }
            raise ValidationError(data)


class OtmUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otm
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('kod'):
            data = {'kod': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('area_located'):
            data = {'area_located': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('city'):
            data = {'city': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('phone'):
            data = {'phone': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('stir'):
            data = {'stir': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('rektor'):
            data = {'rektor': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('ownership'):
            data = {'ownership': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('universityForm'):
            data = {'universityForm': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('address'):
            data = {'address': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('bank_info'):
            data = {'bank_info': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('akkreditasiya_info'):
            data = {'akkreditasiya_info': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs

    def validate_phone(self, phone):
        phone_regex = re.compile(r"^\+998[35789]\d{8}$")
        if re.fullmatch(phone_regex, phone):
            return phone
        else:
            data = {
                "status": False,
                'message': "Contact nomeri to'g'ri kiritilmadi!"
            }
            raise ValidationError(data)

    def validate_stir(self, stir):
        if stir.isdigit() and len(stir) >= 9:
            return stir
        else:
            data = {
                "status": False,
                'message': "STIR noto'g'ri kiritildi, kamida 9 ta raqamdan iborat bo'lishi shart!"
            }
            raise ValidationError(data)


class Faculty_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty_type
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class FacultySerializer(serializers.ModelSerializer):
    faculty_type = Faculty_typeSerializer(many=False)

    class Meta:
        model = Faculty
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('kod'):
            data = {'kod': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('faculty_type'):
            data = {'faculty_type': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('status'):
            data = {'status': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class DepartmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(many=False)

    class Meta:
        model = Department
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('kod'):
            data = {'kod': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('faculty'):
            data = {'faculty': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('status'):
            data = {'status': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('kod'):
            data = {'kod': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('status'):
            data = {'status': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class OtmSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtmSection
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
