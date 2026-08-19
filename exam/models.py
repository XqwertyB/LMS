import datetime

from django.db import models
from django.db.models import F, fields, ExpressionWrapper
from django.utils import timezone

from group.models import Group
from learning_process.models import Curriculum, Educationyear
from semestr.models import Hsemester, Hsemester_action
from shared.models import BaseModel, ExamTypes
from students.models import Student
from subjects.models import Subject


class Exam(BaseModel):
    name = models.CharField(max_length=250, unique=True, blank=True)
    comment = models.TextField(unique=True, blank=True)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    education_year = models.ForeignKey(Educationyear, on_delete=models.CASCADE)
    semester = models.ForeignKey(Hsemester, on_delete=models.CASCADE, null=True)
    exam_type = models.ForeignKey(ExamTypes, on_delete=models.CASCADE, null=True)
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

    def __str__(self):
        return self.name


class ExamStudent(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exams_student', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='students', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='exam_groups_list', blank=True, null=True)
    semester = models.ForeignKey(Hsemester_action, on_delete=models.CASCADE, related_name='semester_action', blank=True,
                                 null=True)
    is_active = models.BooleanField(default=True)
    is_finish = models.BooleanField(default=False)
    is_login = models.BooleanField(default=False)

    class Meta:
        unique_together = ('exam', 'student', 'group')

    def __str__(self):
        return f"{self.student.full_name} {self.is_active}"


class Question(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exams_question')
    name = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Answer(BaseModel):
    name = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    isTrue = models.BooleanField()

    def __str__(self):
        return self.name


class Result(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_students')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='exam_groups')
    ip_address = models.CharField(max_length=20, null=True, blank=True)
    attempts = models.PositiveIntegerField()
    correct_answer = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField()
    max_score = models.PositiveIntegerField()
    begin_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_start = models.BooleanField(default=True)
    exam_time = models.PositiveIntegerField(default=0)
    time_spent = models.BigIntegerField(null=True, blank=True)

    @property
    def percentage(self):
        if self.correct_answer == 0:
            return "0%"
        return f"{(int(self.correct_answer) / int(self.total_count)) * 100:.2f}%"

    @property
    def score(self):
        if self.correct_answer == 0:
            return "0 ball"
        return f"{(int(self.max_score) / int(self.total_count)) * int(self.correct_answer):.0f} ball"

    @property
    def exam_time_second(self):
        if self.time_spent:
            return 0
        else:
            current_time = timezone.now()
            begin_time = self.begin_time
            exam_student = ExamStudent.objects.filter(student=self.student, exam=self.exam).first()
            difference_time = (current_time - begin_time).total_seconds()
            exam_end_time = self.exam.end_time

            if current_time >= exam_end_time:
                self.end_time = timezone.now()
                self.time_spent = int(self.exam_time) * 60
                self.save()
                if exam_student:
                    exam_student.is_finish = True
                    exam_student.is_active = False
                    exam_student.is_login = False
                    exam_student.save()
                return 0

            if current_time < exam_end_time:
                res_time = (exam_end_time - current_time).total_seconds()
                if int(res_time) < int(self.exam_time) * 60:
                    return int(res_time)
                else:
                    if int(self.exam_time) * 60 - int(difference_time) <= 0:
                        self.end_time = timezone.now()
                        self.time_spent = int(self.exam_time) * 60
                        self.save()
                        if exam_student:
                            exam_student.is_finish = True
                            exam_student.is_active = False
                            exam_student.is_login = False
                            exam_student.save()
                        return 0
                    return int(self.exam_time) * 60 - int(difference_time)

    class Meta:
        unique_together = ('exam', 'student', 'group')

    def __str__(self):
        return f"{self.student.full_name}"


class StudentExamAnswer(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_for_answer')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='test_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='questions')
    is_selected = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='answers_select')
    true_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='answers_exam_true')

    def __str__(self):
        return f'{self.exam.name} // {self.student.full_name}'


class StudentForTest(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_for_student')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='students_for_test')
    json_field = models.JSONField()

    def __str__(self):
        return self.exam.name

    class Meta:
        unique_together = ('exam', 'student')
