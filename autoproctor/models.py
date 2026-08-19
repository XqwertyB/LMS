import datetime
import os

from django.db import models

from exam.models import Exam
from shared.models import BaseModel
from students.models import Student


def path_and_rename(instance, filename: str = None):
    upload_to = f'{datetime.date.today()}/{instance.exam.subject.code}/{instance.student.student_id_number}'

    return os.path.join(upload_to, instance.image.name)


class ScreenModel(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam')
    image = models.ImageField(upload_to=path_and_rename)
    attempts = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.student_id_number} {self.exam.name}"
