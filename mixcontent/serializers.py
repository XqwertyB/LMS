from universty.serializers import Faculty_typeSerializer, FacultySerializer
from learning_process.serializers import EducationtypeSerializer, Science_branchSerializer
from speciality.serializers import BspecialitySerializer, MspecialitySerializer, OspecialitySerializer
from rest_framework import serializers, status
from .models import ConnectSpeciality
from rest_framework.exceptions import ValidationError
import re


class ConnectSpecialitySerializer(serializers.ModelSerializer):
    localitytype = Faculty_typeSerializer(many=False, read_only=True)
    educationtype = EducationtypeSerializer(many=False, read_only=True)
    department = FacultySerializer(many=False, read_only=True)
    bachelorSpecialty = BspecialitySerializer(many=False, read_only=True)
    masterSpecialty = MspecialitySerializer(many=False, read_only=True)
    doctorateSpecialty = Science_branchSerializer(many=False, read_only=True)
    ordinatureSpecialty = OspecialitySerializer(many=False, read_only=True)

    class Meta:
        model = ConnectSpeciality
        fields = '__all__'
