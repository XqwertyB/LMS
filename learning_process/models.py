from django.db import models
import uuid
# Create your models here.
from shared.models import BaseModel
from speciality.models import Bspeciality,AllSpeciality
from universty.models import Faculty


class Educationyear(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    current = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Educationtype(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Educationform(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class MarkingSystem(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    minimum_limit = models.PositiveSmallIntegerField()
    gpa_limit = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return self.name


class Curriculum(BaseModel, models.Model):
    cur_id = models.IntegerField(null=True, unique=True)
    name = models.CharField(max_length=250)
    specialty = models.ForeignKey(Bspeciality, on_delete=models.SET_NULL,null=True, related_name='cur_specialty')
    new_specialty = models.ForeignKey(AllSpeciality,on_delete=models.SET_NULL,null=True,related_name='all_specialty_curl')
    educationyear = models.ForeignKey(Educationyear, on_delete=models.CASCADE, related_name='cur_educationyear')
    educationtype = models.ForeignKey(Educationtype, on_delete=models.CASCADE, related_name='cur_educationtype')
    educationform = models.ForeignKey(Educationform, on_delete=models.CASCADE, related_name='cur_educationform')
    markingsystem = models.ForeignKey(MarkingSystem, on_delete=models.CASCADE, related_name='cur_markingsystem')
    semester_count = models.PositiveSmallIntegerField()
    education_period = models.PositiveSmallIntegerField()
    department = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Science_branch(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Educationlang(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name
