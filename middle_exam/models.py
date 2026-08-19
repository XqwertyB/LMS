from django.db import models
from group.models import Group
from learning_process.models import Curriculum, Educationyear
from semestr.models import Hsemester, Hsemester_action
from shared.models import BaseModel, ExamTypes
from students.models import Student
from subjects.models import Subject
from employee.models import Employee
from content.models import Content_teacher

class Middle_exam(BaseModel):
    name = models.CharField(max_length=150)
    comment = models.TextField(unique=True, blank=True)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    semester = models.ForeignKey(Hsemester, on_delete=models.CASCADE, null=True)
    exam_status = models.BooleanField(default=False)
    begin_time = models.DateTimeField(blank=True)
    end_time = models.DateTimeField(blank=True)
    exam_time = models.PositiveIntegerField()
    max_score = models.PositiveIntegerField()
    attempts = models.PositiveIntegerField()
    total_count = models.PositiveIntegerField()
    is_random = models.BooleanField(default=True)
    is_start = models.BooleanField(default=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Employee,on_delete=models.CASCADE)
    connect = models.ForeignKey(Content_teacher,on_delete=models.CASCADE)
    exam_type_name = [
        (True, 'Test shaklida'),
        (False, 'Topshiriq shaklida')
    ]
    exam_type = models.BooleanField(choices=exam_type_name,null=True,blank=True)
    def __str__(self):
        return self.name


class Middle_exam_Student(BaseModel):
    middle_exam = models.ForeignKey(Middle_exam, on_delete=models.CASCADE, related_name='middle_exams_student', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='middle_students', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='middle_exam_groups_list', blank=True, null=True)
    semester = models.ForeignKey(Hsemester_action, on_delete=models.CASCADE, related_name='middle_semester_action', blank=True,
                                 null=True)
    is_active = models.BooleanField(default=True)
    is_finish = models.BooleanField(default=False)
    is_login = models.BooleanField(default=False)

    class Meta:
        unique_together = ('middle_exam', 'student', 'group')

    def __str__(self):
        return f"{self.student.full_name} {self.is_active}"




    