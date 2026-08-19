from django.db import models
from shared.models import BaseModel, ExamTypes, TrainingType
from learning_process.models import Educationtype, Curriculum
from universty.models import Department
from semestr.models import Hsemester


# Create your models here.

class Subjectgroup(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Subject(BaseModel, models.Model):
    hemis_id = models.BigIntegerField(unique=True)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=250)
    status_name = [
        (True, 'Faol'),
        (False, 'Faol emas')
    ]
    subjectgroup = models.ForeignKey(Subjectgroup, on_delete=models.CASCADE, related_name='subjectgroup')
    sub_educationtype = models.ForeignKey(Educationtype, on_delete=models.CASCADE, related_name='sub_educationtype')

    def __str__(self):
        return self.name


class Subject_type(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Subject_block(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Subject_exam_finish(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class RatingGrade(BaseModel, models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Subject_Curriculum(BaseModel, models.Model):
    hemis_id = models.BigIntegerField(unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject')
    subject_type = models.ForeignKey(Subject_type, on_delete=models.CASCADE, related_name='subject_type')
    subject_block = models.ForeignKey(Subject_block, on_delete=models.CASCADE, related_name='subject_block')
    exam_finish = models.ForeignKey(Subject_exam_finish, on_delete=models.CASCADE, related_name='exam_finish')
    subject_departmant = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subject_departmant')
    subject_semestr = models.ForeignKey(Hsemester, on_delete=models.CASCADE, related_name='subject_semestr')
    subject_curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='subject_curriculum')
    ratingGrade = models.ForeignKey(RatingGrade, on_delete=models.CASCADE, related_name='subject_ratingGrade',
                                    null=True)
    total_acload = models.IntegerField(null=True, blank=True)
    resource_count = models.IntegerField(null=True, blank=True)
    credit = models.IntegerField(null=True, blank=True)


class SubjectDetails(BaseModel, models.Model):
    hemis_id = models.BigIntegerField(unique=True)
    trainingType = models.ForeignKey(TrainingType,on_delete=models.CASCADE, null=True, blank=True)
    academic_load = models.PositiveBigIntegerField(null=True,blank=True)
    subject_details = models.ForeignKey(Subject_Curriculum,on_delete=models.CASCADE,null=True,blank=True,related_name='sub_detail')

class SubjectExamTypes(BaseModel,models.Model):
    hemis_id = models.BigIntegerField(unique=True)
    examType = models.ForeignKey(ExamTypes, on_delete=models.CASCADE, null=True, blank=True)
    max_ball = models.PositiveIntegerField(null=True, blank=True)
    sub_exam_type = models.ForeignKey(Subject_Curriculum,on_delete=models.CASCADE,null=True,blank=True,related_name='sub_exam_type')