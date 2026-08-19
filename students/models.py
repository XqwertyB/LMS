from django.db import models

from group.models import Group
from learning_process.models import Educationform, Educationtype, Educationlang, Educationyear
from semestr.models import HCourse, Hsemester_action
from shared.models import BaseModel, H_Student_Status, FormOfPayment, H_Social_Category, H_Accommodation, \
    H_Citizenship_type, Gender, State
from speciality.models import Bspeciality, AllSpeciality
from universty.models import (
    Faculty, City
)
from user.models import User


class Student(BaseModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='student', null=True, blank=True)
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    third_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=150)
    student_id_number = models.CharField(max_length=25)
    image = models.URLField(null=True, blank=True, editable=False)
    birth_date = models.BigIntegerField()
    passport_pin = models.CharField(max_length=14, null=True, blank=True)
    passport_number = models.CharField(max_length=9, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, related_name='student_gender')
    specialty = models.ForeignKey(Bspeciality, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='student_specialty')
    new_specialty = models.ForeignKey(AllSpeciality, on_delete=models.SET_NULL, null=True,
                                      related_name='student_all_specialty')
    studentStatus = models.ForeignKey(H_Student_Status, on_delete=models.CASCADE, related_name='student_studentStatus')
    educationForm = models.ForeignKey(Educationform, on_delete=models.CASCADE, related_name='student_educationForm')
    educationType = models.ForeignKey(Educationtype, on_delete=models.CASCADE, related_name='student_educationType')
    educationYear = models.ForeignKey(Educationyear, on_delete=models.CASCADE, related_name='student_educationYear')
    paymentForm = models.ForeignKey(FormOfPayment, on_delete=models.CASCADE, related_name='student_paymentForm')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='student_group')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='student_faculty')
    educationLang = models.ForeignKey(Educationlang, on_delete=models.SET_NULL, null=True,
                                      related_name='student_educationLang')
    level = models.ForeignKey(HCourse, on_delete=models.CASCADE, related_name='student_level')
    semester = models.ForeignKey(Hsemester_action, on_delete=models.CASCADE, related_name='student_semester')
    country = models.ForeignKey(State, on_delete=models.CASCADE, related_name='student_country')
    province = models.ForeignKey(City, on_delete=models.CASCADE, related_name='student_province')
    district = models.ForeignKey(City, on_delete=models.CASCADE, related_name='student_district')
    citizenship = models.ForeignKey(H_Citizenship_type, on_delete=models.CASCADE, related_name='student_citizenship')
    socialCategory = models.ForeignKey(H_Social_Category, on_delete=models.CASCADE,
                                       related_name='student_socialCategory')
    accommodation = models.ForeignKey(H_Accommodation, on_delete=models.CASCADE, related_name='student_accommodation')
    university = models.CharField(max_length=250, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    validateUrl = models.URLField(null=True, blank=True)
    year_of_enter = models.CharField(max_length=5)
    avg_gpa = models.FloatField(default=0)
    total_credit = models.FloatField(default=0)
    role = models.CharField(max_length=25, default='student', editable=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % self.full_name
