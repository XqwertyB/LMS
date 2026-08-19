import os

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from content.models import Topic, Video_content, File_content, Task_students, Task, Task_type, Student_file, Content, \
    Task_file, LessonRoom, Content_teacher
from bigbluebutton.models import Bigbluebutton_Model
import uuid
from students.serializers import StudentSerializer
from group.serializers import GroupSerializer
from django.utils import timezone
from group.models import Group
from universty.models import Faculty
from learning_process.models import Educationlang, Curriculum, Educationform
from students.models import Student
from django.conf import settings
from employee.models import Employee
from subjects.models import Subject
from shared.models import TrainingType


class Teacher_VideoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Video_content
        fields = ['id', 'name', 'vide_file']


class Student_fileSerializers(serializers.ModelSerializer):
    class Meta:
        model = Student_file
        fields = ['id', 'number', 'student_file', 'file_date_sending', 'comment']


class Teacher_File_contentSerializers(serializers.ModelSerializer):
    class Meta:
        model = File_content
        fields = ['id', 'name', 'file_file']


class Teacher_TopicSerializers(serializers.ModelSerializer):
    topic_files = Teacher_File_contentSerializers(many=True, read_only=True)
    topic_videos = Teacher_VideoSerializers(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'name', 'topic_files', 'topic_videos', 'teacher_id', 'content_teacher_connect', 'in_progress',
                  'topic_bigbluebutton']


class Teacher_VideoCreateSerializers(serializers.ModelSerializer):
    vide_file = serializers.FileField(max_length=512)

    class Meta:
        model = Video_content
        fields = ['id', 'name', 'vide_file', 'video_id_topic', 'teacher_id']


class Teacher_FileCreateSerializers(serializers.ModelSerializer):
    file_file = serializers.FileField(max_length=512)

    class Meta:
        model = File_content
        fields = ['id', 'name', 'file_file', 'file_id_topic', 'teacher_id']


def validate_file_size(value):
    # Set your desired maximum file size in bytes
    max_size = 629145600  # 500MB

    if value.size > max_size:
        raise serializers.ValidationError(
            {
                'status': False,
                'message': 'Video file hajmi 600MB oshishi kerak emas!'
            }

        )


def validate_ffile_size(value):
    # Set your desired maximum file size in bytes
    max_size = 26214400  # 25MB

    if value.size > max_size:
        raise serializers.ValidationError({
            'status': False,
            'message': 'File hajmi 25MB oshishi kerak emas!'
        })


def validate_tfile_size(value):
    # Set your desired maximum file size in bytes
    max_size = 26214400  # 25MB

    if value.size > max_size:
        raise serializers.ValidationError({
            'status': False,
            'message': 'File hajmi 25MB oshishi kerak emas!'
        })
def validate_video_extension(value):
    allowed_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in allowed_extensions:
        raise serializers.ValidationError(
            f"Video formati noto‘g‘ri! Ruxsat etilgan formatlar: {', '.join(allowed_extensions)}"
        )

    return value

class OwenVideAddSerializers(serializers.Serializer):
    topic_id = serializers.UUIDField()
    teacher_id = serializers.CharField()
    video = serializers.FileField(max_length=512, validators=[validate_file_size,validate_video_extension])
    name = serializers.CharField()

def validate_document_extension(value):
    allowed_extensions = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.ppt', '.pptx', '.txt'
    ]
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in allowed_extensions:
        raise serializers.ValidationError(
            f"Fayl formati noto‘g‘ri! Ruxsat etilgan formatlar: {', '.join(allowed_extensions)}"
        )

    return value

class OwenFileAddSerializers(serializers.Serializer):
    topic_id = serializers.UUIDField()
    teacher_id = serializers.CharField()
    files = serializers.FileField(max_length=512, validators=[validate_ffile_size,validate_document_extension])
    name = serializers.CharField()


class BigbluebuttonCreateSerial(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    maxParticipants = serializers.IntegerField(required=False)
    topic_id = serializers.UUIDField()
    teacher_id = serializers.IntegerField()


class Task_typeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task_type
        fields = ['id', 'name', 'code']


class TaskListSerializer(serializers.ModelSerializer):
    task_id_type = Task_typeListSerializer(read_only=True, many=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'comment', 'start_date', 'end_date', 'task_id_type', 'score',
                  'teacher_id']


class Task_studentsSerializer(serializers.ModelSerializer):
    tasks_id = TaskListSerializer(read_only=True, many=False)
    task_student_id = StudentSerializer(read_only=True, many=False)
    task_group_id = GroupSerializer(read_only=True, many=False)
    student_task_fayls = Student_fileSerializers(read_only=True, many=True)

    class Meta:
        model = Task_students
        fields = ['id', 'task_group_id', 'task_student_id', 'tasks_id', 'teacher_id', 'mark',
                  'mark_date', 'mark_status', 'student_task_fayls']


class Task_mark_studentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    task_id = serializers.UUIDField()
    teacher_id = serializers.CharField()
    task_student_id = serializers.UUIDField()
    mark = serializers.IntegerField()
    comment = serializers.CharField()

    def validate(self, data):
        student_id = data.get('student_id', None)
        task_id = data.get('task_id', None)
        mark = data.get('mark', None)
        teacher_id = data.get('teacher_id', None)
        task_student_id = data.get('task_student_id', None)
        comment = data.get('comment', None)
        if student_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Student kiritish majburiy..."
                }
            )
        if task_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq kiritish majburiy..."
                }
            )
        if mark is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Student bahosi kiritish majburiy..."
                }
            )
        if teacher_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Student bahosi kiritish majburiy..."
                }
            )
        if task_student_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq bilan student boglanish kiritish majburiy..."
                }
            )
        if comment is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshriq izoh yozish kerak kiritish majburiy..."
                }
            )
        return data


class ContentviewSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject_id.name', read_only=True)
    curriculum_name = serializers.CharField(source='curriculum_id.name', read_only=True)
    semestr = serializers.CharField(source='content_semestrs.name', read_only=True)

    class Meta:
        model = Content
        fields = [
            'id', 'subject_name', 'curriculum_name', 'semestr'
        ]


class TopicviewSerializer(serializers.ModelSerializer):
    content_id_topic = ContentviewSerializer(many=False)

    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'in_progress', 'content_id_topic'
        ]


class Task_fileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task_file
        fields = [
            'id', 'task_file'
        ]


class TaskviewSerializer(serializers.ModelSerializer):
    topic_id_task = TopicviewSerializer(many=False)
    task_file_count = serializers.SerializerMethodField()
    task_files = Task_fileSerializer(many=True, read_only=True)
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'comment', 'start_date', 'end_date', 'score', 'attempts',
            'topic_id_task', 'task_file_count', 'task_files', 'file_status', 'groups', 'change_session', 'group_status'
        ]

    def get_task_file_count(self, obj):
        if obj.task_files.count() <= 0:
            obj.file_status = False
            obj.save()
        else:
            obj.file_status = True
            obj.save()
        return obj.task_files.count()

    def get_groups(self, obj):
        groups = Group.objects.filter(task_group_list__tasks_id=obj).distinct()
        return [
            {
                'id': group.id,
                'name': group.name,
                'faculty': group.faculty.name,
                'educationLang': group.educationLang.name
            }
            for group in groups]


class TaskcreateSerializer(serializers.ModelSerializer):
    task_file_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'topic_id_task', 'name', 'comment', 'start_date',
            'end_date', 'score', 'teacher_id', 'attempts', 'task_file_count', 'file_status', 'group_status'
        ]

    def validate(self, data):
        current_datetime = timezone.now()
        topic_id_task = data.get('topic_id_task', None)
        name = data.get('name', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        score = data.get('score', None)
        teacher_id = data.get('teacher_id', None)
        attempts = data.get('attempts', None)
        if topic_id_task is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzular id kirtilishi majburiy..."
                }
            )
        if name is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq nomi kiritish majburiy..."
                }
            )
        if start_date is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni boshlanish vaqtini kiritish majburiy..."
                }
            )

        if start_date < current_datetime:
            raise serializers.ValidationError({
                'status': False,
                "message": "Topshiriqni boshlanish vaqti joriy vaqtdan kichik bo'lishi mumkin emas"
            })

        if end_date is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni tugash vaqtini kiritish majburiy..."
                }
            )
        if end_date < current_datetime:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni tugash vaqti joriy vaqtdan kichik bo'lishi mumkin emas"
                }
            )
        if start_date >= end_date:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni tugash vaqti boshlanish vaqtidan yuqori bo`lish kere"
                }
            )
        if score is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq balni kiritish majburiy..."
                }
            )
        if teacher_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "O`qtuvchini kiritish  majburiy..."
                }
            )
        if attempts is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq urinishlar soni kiritish majburiy..."
                }
            )
        if int(score) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan ball qiymay manfi, faqat musbat qabul qiladi."
                }
            )
        if int(score) >= topic_id_task.content_id_topic.totatl_score_jn:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan ball qiymay Joriy ballardan yuqori."
                }
            )
        try:
            summa = 0
            topics = topic_id_task.content_id_topic.content_set_topic.all()
            for item in topics:
                if item.topic_set_task:
                    for var in item.topic_set_task.all():
                        summa += var.score

        except Exception as ex:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": str(ex)
                }
            )
        if int(score) + summa > topic_id_task.content_id_topic.totatl_score_jn:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan ball qiymay jami topshiriqlar bilan qo`shganda Joriy ballardan o`tib ketmoqda.",
                    "Topshiriqlar jammi ballar": summa,
                    "Asosiy joriy ball": topic_id_task.content_id_topic.totatl_score_jn,
                    "Hozirgi kirtilgan ball": score,
                    "Qo`yish mumkin ball": topic_id_task.content_id_topic.totatl_score_jn - summa
                }
            )
        return data

    def get_task_file_count(self, obj):
        if obj.task_files.count() <= 0:
            obj.file_status = False
            obj.save()
        else:
            obj.file_status = True
            obj.save()
        return obj.task_files.count()


class TaskcreatesxemSerializer(serializers.Serializer):
    topic_id_task = serializers.UUIDField()
    name = serializers.CharField(max_length=250)
    comment = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    score = serializers.IntegerField()
    teacher_id = serializers.IntegerField()
    attempts = serializers.IntegerField()


class Task_file_add_sxemSerializer(serializers.Serializer):
    task_files = serializers.ListField(child=serializers.FileField())


class TaskallsxemSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    topic_id = serializers.UUIDField()


class EducationlangGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educationlang
        fields = [
            'id', 'name'
        ]


class FacultygroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = [
            'id', 'name'
        ]


class Task_groupSerializer(serializers.ModelSerializer):
    faculty = FacultygroupSerializer()
    educationLang = EducationlangGroupSerializer()

    class Meta:
        model = Group
        fields = [
            'id', 'h_id', 'name', 'group_curriculum', 'faculty', 'specialty', 'educationLang'
        ]


class TaskgroupsxemSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    task_id = serializers.UUIDField()


class TaskstudentsxemSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    group_id = serializers.UUIDField()


class TaskStudentSerializer(serializers.ModelSerializer):
    group = Task_groupSerializer()

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'second_name', 'third_name', 'full_name', 'group', 'student_task_action'
        ]


class TaskGorupAddSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    groups = serializers.ListField(
        child=serializers.UUIDField()
    )

    def validate(self, data):
        teacher_id = data.get('teacher_id', None)
        groups = data.get('groups', None)
        if teacher_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "O`qtuvchi id kirtilishi majburiy..."
                }
            )
        if groups is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Guruhlar id kirtilishi majburiy..."
                }
            )
        return data


class Taskcreatewithfile(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'topic_id_task', 'name', 'comment', 'start_date',
            'end_date', 'score', 'teacher_id', 'attempts', 'file_status', 'group_status'
        ]

    def validate(self, data):
        current_datetime = timezone.now()
        topic_id_task = data.get('topic_id_task', None)
        name = data.get('name', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        score = data.get('score', None)
        teacher_id = data.get('teacher_id', None)
        attempts = data.get('attempts', None)

        if topic_id_task is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzular id kirtilishi majburiy..."
                }
            )
        if name is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq nomi kiritish majburiy..."
                }
            )
        if start_date is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni boshlanish vaqtini kiritish majburiy..."
                }
            )

        if start_date < current_datetime:
            raise serializers.ValidationError({
                'status': False,
                "message": "Topshiriqni boshlanish vaqti joriy vaqtdan kichik bo'lishi mumkin emas"
            })

        if end_date is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni tugash vaqtini kiritish majburiy..."
                }
            )
        if end_date < current_datetime:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni tugash vaqti joriy vaqtdan kichik bo'lishi mumkin emas"
                }
            )
        if start_date >= end_date:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqni tugash vaqti boshlanish vaqtidan yuqori bo`lish kere"
                }
            )
        if score is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq balni kiritish majburiy..."
                }
            )
        if teacher_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "O`qtuvchini kiritish  majburiy..."
                }
            )
        if attempts is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq urinishlar soni kiritish majburiy..."
                }
            )
        if int(score) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan ball qiymay manfi, faqat musbat qabul qiladi."
                }
            )
        try:
            summa = 0
            topics = topic_id_task.content_id_topic.content_set_topic.all()
            for item in topics:
                if item.topic_set_task:
                    for var in item.topic_set_task.all():
                        summa += var.score
        except Exception as ex:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": str(ex)
                }
            )

        if int(score) + summa > topic_id_task.content_teacher_connect.totatl_score_jn:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan ball qiymay jami topshiriqlar bilan qo`shganda Joriy ballardan o`tib ketmoqda.",
                    "Topshiriqlar jammi ballar": summa,
                    "Asosiy joriy ball": topic_id_task.content_teacher_connect.totatl_score_jn,
                    "Hozirgi kirtilgan ball": score,
                    "Qo`yish mumkin ball": topic_id_task.content_teacher_connect.totatl_score_jn - summa
                }
            )
        return data


class TaskFilecreateSerializer(serializers.Serializer):
    task_files = serializers.ListField(
        child=serializers.FileField()
    )
    task_id = serializers.UUIDField()
    task = serializers.SerializerMethodField()

    def validate(self, data):
        task_files = data.get('task_files', None)
        task_id = data.get('task_id', None)
        if task_files is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq faylari kirtilishi majburiy..."
                }
            )
        if task_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiq yartilishda muamo sodir bo`ldi... "
                }
            )
        try:
            obj_task = Task.objects.get(id=task_id)
        except Exception as ex:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiq topilmadi."
                }
            )
        max_file_size = getattr(settings, "MAX_FILE_SIZE", 25 * 1024 * 1024)  # Default max file size is 25MB
        for file in task_files:
            if file.size > max_file_size:
                raise serializers.ValidationError({
                    'status': False,
                    "message": f" File hajmi 25MB oshishi kerak emas! Bu file {file.name} hajmi 25MB oshgan"
                })
        return data

    def get_task(self, validated_data):
        return Task.objects.get(id=validated_data.get('task_id'))

    def create(self, validated_data, **kwargs):
        task_files = validated_data.get('task_files')
        obj_task = self.get_task(validated_data)

        for file in task_files:
            try:
                obj_task_file = Task_file()
                obj_task_file.task_file = file
                obj_task_file.task = obj_task
                obj_task_file.save()

            except Exception as ex:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        "message": "Topshiriq fayilarini saqlash muamo mavjud...",
                        'error': str(ex)
                    }
                )
        return self.validated_data


class TaskFilescreateschemaSerializer(serializers.Serializer):
    topic_id_task = serializers.UUIDField()
    name = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    score = serializers.IntegerField()
    teacher_id = serializers.IntegerField()
    attempts = serializers.IntegerField()
    task_files = serializers.ListField(
        child=serializers.FileField()
    )


class TaskactionSerializer(serializers.ModelSerializer):
    task_group_id = GroupSerializer()
    task_student_id = TaskStudentSerializer()

    class Meta:
        model = Task_students
        fields = [
            'id', 'task_group_id', 'task_student_id', 'tasks_id', 'time_status', 'status_control',
            'uploading_file_status'
        ]


class TaskFUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'topic_id_task', 'name', 'comment', 'start_date',
            'end_date', 'score', 'teacher_id', 'attempts', 'file_status', 'change_session', 'group_status',
            'task_students'
        ]

    def update(self, instance, validated_data):
        current_datetime = timezone.now()
        instance.topic_id_task = validated_data.get('topic_id_task', instance.topic_id_task)
        instance.name = validated_data.get('name', instance.name)
        instance.score = validated_data.get('score', instance.score)
        instance.teacher_id = validated_data.get('teacher_id', instance.teacher_id)
        instance.attempts = validated_data.get('attempts', instance.attempts)
        instance.comment = validated_data.get('comment', instance.comment)
        change_session = instance.change_session
        students = instance.task_students.all()
        for student in students:
            if student.uploading_file_status:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        'message': "Bu topshiriqni o`zgartib bo`lmidi bir talaba tomonidan ma`lumot yuklangan"
                    }
                )
            if student.mark_status:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        'message': "Bu topshiriqni o`zgartib bo`lmidi bir talabaga baholangan"
                    }
                )
        if int(instance.score) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    'message': "Kirtilgan ball qiymay manfi, faqat musbat qabul qiladi."
                }
            )
        try:
            summa = 0
            topics = instance.topic_id_task.content_id_topic.content_set_topic.all()
            for item in topics:
                if item.topic_set_task:
                    for var in item.topic_set_task.all():
                        summa += var.score
        except Exception as ex:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": str(ex)
                }
            )
        if int(instance.score) + summa > instance.topic_id_task.content_teacher_connect.totatl_score_jn:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan ball qiymay jami topshiriqlar bilan qo`shganda Joriy ballardan o`tib ketmoqda."
                    # "Topshiriqlar jammi ballar": str(summa),
                    # "Asosiy joriy ball": str(instance.topic_id_task.content_id_topic.totatl_score_jn),
                    # "Hozirgi kirtilgan ball": str(instance.score),
                    # "Qo`yish mumkin ball": str(instance.topic_id_task.content_id_topic.totatl_score_jn - summa)
                }
            )
        if instance.attempts == 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq urinishlar 0ga teng bo`lolmaydi..."
                }
            )
        # print(change_session)
        if change_session:
            instance.start_date = validated_data.get('start_date', instance.start_date)
            instance.end_date = validated_data.get('end_date', instance.end_date)
            if instance.end_date < current_datetime:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        "message": "Topshiriqni tugash vaqti joriy vaqtdan kichik bo'lishi mumkin emas"
                    }
                )
            if instance.start_date >= instance.end_date:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        "message": "Topshiriqni tugash vaqti boshlanish vaqtidan yuqori bo`lish kere"
                    }
                )

        instance.save()
        return instance


class TaskFileupdateSerializer(serializers.Serializer):
    task_files = serializers.ListField(
        child=serializers.FileField(validators=[validate_tfile_size]), required=False
    )

    def validate(self, attrs):
        task_fiels = attrs.get('task_fiels')

        return attrs


class Task_studentsListSerializer(serializers.ModelSerializer):
    student_task_fayls = Student_fileSerializers(read_only=True, many=True)
    task_student_id = StudentSerializer()
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = Task_students
        fields = ['id', 'task_student_id', 'teacher_id', 'mark',
                  'mark_date', 'mark_status', 'student_task_fayls', 'uploading_file_status',
                  'status_control', 'time_status', 'number_status', 'checking_status', 'total_score']

    def get_total_score(self, obj):
        return obj.tasks_id.score


class StudnetgetGorupingSerializer(serializers.ModelSerializer):
    task_group_list = Task_studentsListSerializer(many=True)

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'task_group_list'
        ]


class GetScorelimitSerailizer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    task_id = serializers.UUIDField()


class GetScoreTopiclimitSerailizer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    topic_id = serializers.UUIDField()


class RoomLessonUpdateSerializer(serializers.ModelSerializer):
    connect = serializers.ListSerializer(child=serializers.UUIDField(), required=False)

    class Meta:
        model = LessonRoom
        fields = ['name', 'connect', 'is_active']

    def validate(self, attrs):
        # Get the attributes
        name = attrs.get('name', None)
        connect = attrs.get('connect', None)

        # Validation checks
        if name is None:
            raise ValidationError({
                'error': True,
                'message': 'Nomi bo`sh bo`lish kerakmas!'
            })
        if connect is None:
            raise ValidationError({
                'error': True,
                'message': 'Guruhlar jamlanmalari bo`sh bo`lish kerakmas!'
            })

        return attrs

    def update(self, instance, validated_data):
        # Extract 'connect' and 'teacher_id' from validated_data
        connect_data = validated_data.pop('connect', None)

        # Update LessonRoom fields
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        # Handle connect updates (ManyToMany relationships)
        if connect_data:
            instance.connect.clear()  # Clear existing relationships
            for uuid in connect_data:
                try:
                    connected_instance = Content_teacher.objects.get(id=uuid)
                    instance.connect.add(connected_instance)
                except Content_teacher.DoesNotExist:
                    raise serializers.ValidationError({
                        'error': True,
                        'message': f'Connect object with id {uuid} topilmadi.'
                    })

        # Save the updated instance
        instance.save()
        return instance


class Teacher_Info_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 'full_name'
        ]


class Educationform_Info_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Educationform
        fields = ['id', 'code', 'name']


class Curriculum_Info_Seralizer(serializers.ModelSerializer):
    educationform = Educationform_Info_Serializer()

    class Meta:
        model = Curriculum
        fields = ['name', 'educationform']


class Subject_Info_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            'id', 'code', 'name'
        ]


class Content_subject_Serializer(serializers.ModelSerializer):
    subject_id = Subject_Info_Serializer()
    curriculum_id = Curriculum_Info_Seralizer()

    class Meta:
        model = Content
        fields = [
            'id', 'subject_id', 'curriculum_id', 'semestr_action'
        ]


class EduLang_Info_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Educationlang
        fields = [
            'id', 'code', 'name'
        ]


class Training_type_Info_Serializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingType
        fields = [
            'id', 'code', 'name'
        ]


class Group_list_Info_Serializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'student_count'
        ]

    def get_student_count(self, obj):
        try:
            result = obj.student_group.all().count()
            return result
        except Exception as ex:
            return 0


class Content_teacherList_Serializer(serializers.ModelSerializer):
    teacher_id = Teacher_Info_Serializer()
    content_id = Content_subject_Serializer()
    group_lang = EduLang_Info_Serializer()
    group_by = Group_list_Info_Serializer(many=True)
    training_type = Training_type_Info_Serializer()

    class Meta:
        model = Content_teacher
        fields = [
            'id', 'teacher_id', 'content_id', 'group_lang', 'group_by', 'training_type'
        ]


class Connect_list_Serializer(serializers.ModelSerializer):
    content_id = Content_subject_Serializer()  # No 'many=True' for ForeignKey
    group_lang = EduLang_Info_Serializer()
    group_by = Group_list_Info_Serializer(many=True)
    training_type = Training_type_Info_Serializer()

    class Meta:
        model = Content_teacher
        fields = [
            'id', 'content_id', 'group_lang', 'group_by', 'training_type'
        ]


class LessonRoomListSerialzier(serializers.ModelSerializer):
    connect = Connect_list_Serializer(many=True)

    class Meta:
        model = LessonRoom
        fields = ['id', 'name', 'connect', 'teacher_id', 'is_active', 'team_bigbluebutton','start_datetime']


class LessonRoomCreateSerialzer(serializers.ModelSerializer):
    teacher_id = serializers.UUIDField()
    connect = serializers.ListSerializer(child=serializers.UUIDField())

    class Meta:
        model = LessonRoom
        fields = ['name', 'connect', 'teacher_id', 'is_active','start_datetime']

    def validate(self, attrs):
        name = attrs.get('name', None)
        connect = attrs.get('connect', None)
        teacher_id = attrs.get('teacher_id', None)

        if name is None:
            raise ValidationError({
                'error': True,
                'message': 'Nomi bo`sh bo`lish kerakmas!'
            })
        if connect is None:
            raise ValidationError({
                'error': True,
                'message': 'Guruhlar jamlanmalari bo`sh bo`lish kerakmas!'
            })
        if teacher_id is None:
            raise ValidationError({
                'error': True,
                'message': 'O`qtuvchi bo`sh bo`lish kerakmas!'
            })

        return attrs

    def create(self, validated_data):
        # Extract the connect field from validated_data
        connect_data = validated_data.pop('connect', [])

        # Fetch the Employee instance using the teacher_id UUID
        teacher_uuid = validated_data.pop('teacher_id')
        try:
            teacher = Employee.objects.get(id=teacher_uuid)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({
                'error': True,
                'message': 'O`qtuvchi topilmadi.'
            })

        # Create the LessonRoom object with the fetched Employee instance
        lesson_room = LessonRoom.objects.create(teacher_id=teacher, **validated_data)

        # Assuming 'connect' is a ManyToMany field or a ForeignKey relationship
        for uuid in connect_data:
            connected_instance = Content_teacher.objects.get(
                id=uuid)  # Assuming the connect field references another model by UUID
            lesson_room.connect.add(connected_instance)  # Add to the ManyToMany relationship

        return lesson_room
