import os
import uuid

from django.db import models
from shared.models import BaseModel, TrainingType
# Create your models here.
from subjects.models import Subject
from learning_process.models import Educationtype, Curriculum, Educationyear, Educationlang
from semestr.models import Hsemester, HCourse
from group.models import Group
from students.models import Student
from employee.models import Employee


class Content(BaseModel, models.Model):
    hemis_id = models.BigIntegerField(unique=True, null=True, blank=True)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    curriculum_id = models.ForeignKey(Curriculum, on_delete=models.CASCADE, null=True, blank=True)
    content_semestrs = models.ForeignKey(Hsemester, on_delete=models.CASCADE, null=True, blank=True)
    semestr_action_name = [
        (True, 'Faol'),
        (False, 'Faolemas')
    ]
    semestr_action = models.BooleanField(choices=semestr_action_name, default=False)
    totatl_score_jn = models.PositiveIntegerField(null=True, blank=True)
    totatl_score_on = models.PositiveIntegerField(null=True, blank=True)
    totatl_score_yn = models.PositiveIntegerField(null=True, blank=True)
    total_on_yn_name = [
        (True, 'ON va YN'),
        (False, 'YN')
    ]
    total_score_check = models.BooleanField(default=True, choices=total_on_yn_name)
    group = models.ManyToManyField(Group, blank=True)
    credit = models.IntegerField(null=True, blank=True)
    level = models.ForeignKey(HCourse, on_delete=models.CASCADE, related_name='content_h_level', null=True)

    def __str__(self):
        return self.subject_id.name


class Roletype(BaseModel, models.Model):  # auditoriumType
    name = models.CharField(max_length=75)
    code = models.BigIntegerField(unique=True, null=True, blank=True)
    # 1 Maruzachi, Amaliyotchi


class Content_teacher(BaseModel, models.Model):
    teacher_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='content_teacher')
    content_id = models.ForeignKey(Content, on_delete=models.CASCADE, null=True, related_name='teacher_content')
    group_lang = models.ForeignKey(Educationlang, on_delete=models.CASCADE, null=True)
    group_by = models.ManyToManyField(Group)
    topic_count = models.IntegerField(null=True, blank=True)
    video_count = models.IntegerField(null=True, blank=True)
    task_count = models.IntegerField(null=True, blank=True)
    totatl_score_jn = models.PositiveIntegerField(null=True, blank=True)
    totatl_score_on = models.PositiveIntegerField(null=True, blank=True)
    totatl_score_yn = models.PositiveIntegerField(null=True, blank=True)
    training_type = models.ForeignKey(TrainingType, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher_id', 'content_id', 'group_lang', 'training_type',)


class Content_teacher_log(BaseModel, models.Model):
    old_teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='old_teacher')
    new_teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='new_teacher')
    content_teacher_log = models.ForeignKey(Content_teacher, on_delete=models.CASCADE, null=True, blank=True,
                                            related_name='content_teacher_log')
    comment = models.TextField(null=True, blank=True)
    old_role_type = models.ForeignKey(Roletype, on_delete=models.CASCADE, null=True, related_name='old_role_type')
    new_role_type = models.ForeignKey(Roletype, on_delete=models.CASCADE, null=True, related_name='new_role_type')


class Topic(BaseModel, models.Model):
    name = models.CharField(max_length=250)
    in_progress = models.BooleanField(default=False)
    content_teacher_connect = models.ForeignKey(Content_teacher, on_delete=models.CASCADE, null=True, blank=True,
                                                related_name='content_teacher_connect')
    content_id_topic = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='content_set_topic')
    teacher_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    number = models.PositiveIntegerField(null=True, blank=True)


class Video_content(BaseModel, models.Model):
    name = models.CharField(max_length=250)
    vide_file = models.FileField(upload_to='video_content/')
    video_id_topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='topic_videos')
    teacher_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.vide_file:
            ext = os.path.splitext(self.vide_file.name)[-1]
            self.vide_file.name = f'{uuid.uuid4()}{ext}'

        super(Video_content, self).save(*args, **kwargs)


class File_content(BaseModel, models.Model):
    name = models.CharField(max_length=250)
    file_file = models.FileField(upload_to='file_content/')
    file_id_topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='topic_files')
    teacher_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)


class Task_type(BaseModel, models.Model):
    name = models.CharField(max_length=75)
    code = models.BigIntegerField(unique=True, null=True, blank=True)
    # code = 1 -> topshiriq shakli
    # code = 2 -> test shakli


class Task(BaseModel, models.Model):
    topic_id_task = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, related_name='topic_set_task')
    name = models.CharField(max_length=250)
    comment = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    teacher_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    attempts = models.PositiveIntegerField(null=True, blank=True)
    file_status = models.BooleanField(
        default=False)  # toshiriqga fayil yuklansa ozgaradi va shunga nisbatan tekshriladi
    change_session = models.BooleanField(default=False)  # Supper admin orqali status orqali update qilish imkoni berish
    group_status = models.BooleanField(default=False)  # guruhlar qo`shilmagan bo`lsa nazorati
    # Faol bo`lsa o`zgarish mumkin vaqtlarga oqtuvchi tomonidan
    # Faol bo`lmasa o`zgarmidi oqtuvhi tomonidan vaqtlar


class Task_students(BaseModel, models.Model):
    check_name = [
        (True, 'Talaba kesmida'),
        (False, 'Guruhlar kesmida')
    ]
    task_check = models.BooleanField(choices=check_name, null=True, blank=True)
    task_group_id = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='task_group_list')
    task_student_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='student_task_action')
    tasks_id = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='task_students')
    teacher_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    mark_date = models.DateTimeField(null=True, blank=True)
    mark = models.IntegerField(null=True, blank=True)
    mark_status_name = [
        (True, 'Baholangan'),
        (False, 'Baholanmagan')
    ]
    mark_status = models.BooleanField(default=False,
                                      choices=mark_status_name)  # baholangan yoki baholanmagni ko`rsatish
    checker = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='checker')
    comment = models.TextField(null=True, blank=True)
    status_control_name = [
        (True, 'Ishlash huquqi mavjud'),
        (False, 'Ishlash huquqi mavjudemas')
    ]
    time_status = models.BooleanField(default=True, null=True, blank=True)  # vaqt intervaldagi nazorat uchun
    status_control = models.BooleanField(default=True,
                                         choices=status_control_name)  # to`liq yopib qo`yilish nazorat qilnadi
    is_status = models.BooleanField(default=False)  # pass ball qo`yilgani statusi
    number = models.PositiveIntegerField(null=True, blank=True)
    uploading_file_name = [
        (True, 'Fayil yuklangan!'),
        (False, 'Fayil yuklanmagan!'),
    ]
    uploading_file_status = models.BooleanField(default=False,
                                                choices=uploading_file_name)  # yuklangan fayil status oquvchi tarfdan
    number_status = models.BooleanField(default=False, null=True, blank=True)
    checking_status = models.BooleanField(default=False, null=True, blank=True)
    is_passed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tasks_id', 'task_student_id', 'task_group_id')

    def __str__(self):
        return self.tasks_id.name


class Task_file(BaseModel, models.Model):
    task_file = models.FileField(upload_to='task_files/')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_files')


class Student_file(BaseModel, models.Model):
    student_file = models.FileField(upload_to='student_tasks/', null=True, blank=True)
    file_status_name = [
        (True, 'Fayl yuklangan'),
        (False, 'Fayl yuklanmagan')
    ]
    file_status = models.BooleanField(choices=file_status_name, default=False)
    file_date_sending = models.DateTimeField(null=True, blank=True)
    take_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='student_task_detail')
    task_connect = models.ForeignKey(Task_students, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='student_task_fayls')
    comment = models.TextField(null=True, blank=True)
    student_task_id = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    number = models.PositiveIntegerField(null=True, blank=True)


class LessonRoom(BaseModel):
    name = models.CharField(max_length=250, null=True, blank=True)
    connect = models.ManyToManyField(Content_teacher, related_name='connect_base')
    teacher_id = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='lesson_teacher')
    is_active = models.BooleanField(default=True)
    start_datetime = models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return self.name
