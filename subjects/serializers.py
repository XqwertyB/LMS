from rest_framework import serializers, status

from semestr.serializers import HsemesterSerializer
from .models import Subjectgroup, Subject, Subject_type, Subject_block, Subject_exam_finish, Subject_Curriculum
from rest_framework.exceptions import ValidationError
import re
from learning_process.serializers import EducationtypeSerializer, CurriculumSerializer


class SubjectgroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjectgroup
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


class SubjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('hemis_id'):
            data = {'hemis_id': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('subjectgroup'):
            data = {'subjectgroup': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('sub_educationtype'):
            data = {'sub_educationtype': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs


class SubjectSerializer(serializers.ModelSerializer):
    subjectgroup = SubjectgroupSerializer(many=False, read_only=True)
    sub_educationtype = EducationtypeSerializer(many=False, read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'


class Subject_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject_type
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


class Subject_blockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject_block
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


class Subject_exam_finishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject_exam_finish
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


class Subject_CurriculumSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = Subject_Curriculum
        fields = ['id','subject']


class GetSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class SubjectCurriculumSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Subject_Curriculum
        fields = [
            'id',
            'subject',
            'subject_name',
        ]
