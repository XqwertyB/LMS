from urllib.parse import urlparse, urlunparse

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings
from group.models import Group
from learning_process.models import Educationform, Educationtype, Educationyear, Educationlang, Curriculum
from semestr.models import HCourse, Hsemester_action, Hsemester
from shared.models import Gender, H_Student_Status, FormOfPayment, State, H_Citizenship_type, H_Social_Category, \
    H_Accommodation
from speciality.models import Bspeciality,AllSpeciality
from universty.models import Faculty, City, Faculty_type
from .models import Student


class S_GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['code', 'name']


class S_EducationyearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationyear
        fields = ['code', 'name', 'current']


class S_HsemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hsemester
        fields = ['code', 'name']


class S_BspecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bspeciality
        fields = ['base_spec_id', 'code', 'name']

class S_AllSpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AllSpeciality
        fields = ['spec_id', 'code', 'name']

class S_CurriculumSerializer(serializers.ModelSerializer):
    specialty = S_BspecialitySerializer()
    educationyear = S_EducationyearSerializer()

    class Meta:
        model = Curriculum
        fields = ['cur_id', 'specialty', 'name', 'educationyear']


class S_H_Student_StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = H_Student_Status
        fields = ['id', 'code', 'name']


class S_EducationformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationform
        ref_name = 'StudentEducationformSerializer'
        fields = ['code', 'name']


class S_EducationtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationtype
        fields = ['code', 'name']


class S_FormOfPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormOfPayment
        fields = ['code', 'name']


class S_EducationlangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationlang
        fields = ['code', 'name']


class S_Faculty_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty_type
        fields = ['code', 'name']


class S_FacultySerializer(serializers.ModelSerializer):
    faculty_type = S_Faculty_typeSerializer()

    class Meta:
        model = Faculty
        fields = keys = [
            'name',
            'hemisid',
            'kod',
            'faculty_type'
        ]


class S_GroupSerializer(serializers.ModelSerializer):
    faculty = S_FacultySerializer()
    specialty = S_AllSpecialitySerializer()
    educationLang = S_EducationlangSerializer()
    group_curriculum = S_CurriculumSerializer()

    class Meta:
        model = Group
        fields = ['id', 'name', 'faculty', 'specialty', 'educationLang', 'group_curriculum']


class S_HCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HCourse
        fields = ['code', 'name']


class S_Hsemester_actionSerializer(serializers.ModelSerializer):
    curriculum = S_CurriculumSerializer()
    education_year = S_EducationyearSerializer()
    level = S_HCourseSerializer()
    semester = S_HsemesterSerializer()

    class Meta:
        model = Hsemester_action
        fields = [
            'h_id',
            'curriculum',
            'education_year',
            'current',
            'level',
            'semester'
        ]


class S_StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['code', 'name']


class S_CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['code', 'name', 'parent']


class S_H_Citizenship_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = H_Citizenship_type
        fields = ['code', 'name']


class S_H_Social_CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = H_Social_Category
        fields = ['code', 'name']


class S_H_AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = H_Accommodation
        fields = ['code', 'name']


class S_StudentImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['image']

    def get_image(self, obj):
        image_url = obj.image.url

        request = self.context.get('request')
        if request and request.is_secure():
            url_parts = urlparse(image_url)
            image_url = urlunparse(url_parts._replace(scheme='https'))

        if request is not None:
            return request.build_absolute_uri(image_url)
        return image_url


class StudentSerializer(serializers.ModelSerializer):
    gender = S_GenderSerializer()
    specialty = S_AllSpecialitySerializer()
    studentStatus = S_H_Student_StatusSerializer()
    educationForm = S_EducationformSerializer()
    educationType = S_EducationtypeSerializer()
    educationYear = S_EducationyearSerializer()
    paymentForm = S_FormOfPaymentSerializer()
    group = S_GroupSerializer()
    faculty = S_FacultySerializer()
    educationLang = S_EducationlangSerializer()
    level = S_HCourseSerializer()
    semester = S_Hsemester_actionSerializer()
    country = S_StateSerializer()
    province = S_CitySerializer()
    district = S_CitySerializer()
    citizenship = S_H_Citizenship_typeSerializer()
    socialCategory = S_H_Social_CategorySerializer()
    accommodation = S_H_AccommodationSerializer()

    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'second_name',
            'third_name',
            'full_name',
            'student_id_number',
            'image',
            'birth_date',
            'passport_pin',
            'passport_number',
            'email',
            'phone',
            'gender',
            'university',
            'specialty',
            'studentStatus',
            'educationForm',
            'educationType',
            'educationYear',
            'paymentForm',
            'group',
            'faculty',
            'educationLang',
            'level',
            'semester',
            'address',
            'country',
            'province',
            'district',
            'citizenship',
            'socialCategory',
            'accommodation',
            'validateUrl',
            'year_of_enter',
            'avg_gpa',
            'total_credit',
            'is_active'
        ]


class StudentForResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'full_name'
        ]


class StudentForGroupSerializer(serializers.ModelSerializer):
    gender = S_GenderSerializer()
    specialty = S_AllSpecialitySerializer()
    studentStatus = S_H_Student_StatusSerializer()
    educationForm = S_EducationformSerializer()
    educationType = S_EducationtypeSerializer()
    educationYear = S_EducationyearSerializer()
    paymentForm = S_FormOfPaymentSerializer()
    group = S_GroupSerializer()
    faculty = S_FacultySerializer()
    educationLang = S_EducationlangSerializer()
    level = S_HCourseSerializer()
    semester = S_Hsemester_actionSerializer()
    country = S_StateSerializer()
    province = S_CitySerializer()
    district = S_CitySerializer()
    citizenship = S_H_Citizenship_typeSerializer()
    socialCategory = S_H_Social_CategorySerializer()
    accommodation = S_H_AccommodationSerializer()

    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'second_name',
            'third_name',
            'full_name',
            'student_id_number',
            'image',
            'birth_date',
            'passport_pin',
            'passport_number',
            'email',
            'phone',
            'gender',
            'university',
            'specialty',
            'studentStatus',
            'educationForm',
            'educationType',
            'educationYear',
            'paymentForm',
            'group',
            'faculty',
            'educationLang',
            'level',
            'semester',
            'address',
            'country',
            'province',
            'district',
            'citizenship',
            'socialCategory',
            'accommodation',
            'validateUrl',
            'year_of_enter',
            'avg_gpa',
            'total_credit'
        ]


class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('role',)


class StudentIsActiveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["is_active"]


class StudentLoginSerializer(serializers.Serializer):
    login = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
