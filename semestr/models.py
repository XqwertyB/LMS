from django.db import models
from shared.models import BaseModel
# Create your models here.
from learning_process.models import Curriculum, Educationyear


class HCourse(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Hsemester(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Hsemester_action(BaseModel, models.Model):
    h_id = models.IntegerField(unique=True)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='hcurriculum')
    education_year = models.ForeignKey(Educationyear, on_delete=models.CASCADE, related_name='heducation_year')
    current = models.BooleanField(default=False)
    level = models.ForeignKey(HCourse, on_delete=models.CASCADE, related_name='h_level',null=True)
    semester = models.ForeignKey(Hsemester, on_delete=models.CASCADE, related_name='hsemestr', null=True)

    def __str__(self):
        return self.semester.name

    class Meta:
        unique_together = ('curriculum', 'semester')

class CurriculumWeeks(BaseModel, models.Model):
    msemester = models.ForeignKey(Hsemester_action, on_delete=models.CASCADE, related_name='ha_semester')
    h_id = models.IntegerField(unique=True)
    current = models.BooleanField(default=False)
    start_date = models.BigIntegerField(null=True)
    end_date = models.BigIntegerField(null=True)
    start_date_f = models.DateField()
    end_date_f = models.DateField()

    def __str__(self):
        return str(self.h_id)
