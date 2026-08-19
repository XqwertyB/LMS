from rest_framework import serializers
from content.models import Content, Content_teacher, Topic, Video_content, File_content, Content_teacher, Task, \
    Task_file, Task_students
from employee.models import Employee
from group.models import Group
from speciality.models import Bspeciality
from learning_process.models import Curriculum
from students.models import Student
from django.utils import timezone


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'topic_id_task', 'name', 'comment', 'start_date', 'end_date', 'task_id_type', 'score',
                  'teacher_id']


class TaskbspecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bspeciality
        fields = ['id', 'name']


class TaskCurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'name']


class ConnectGroupSerializers(serializers.ModelSerializer):
    specialty = TaskbspecialitySerializer(read_only=True, many=False)
    group_curriculum = TaskCurriculumSerializer(read_only=True, many=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'h_id', 'specialty', 'group_curriculum']


class StudentsSerializers(serializers.ModelSerializer):
    group = ConnectGroupSerializers(read_only=True, many=False)

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'group']


class CreateTaskWithGroupSerializers(serializers.Serializer):
    topic_id_task = serializers.UUIDField()
    name = serializers.CharField(max_length=250)
    comment = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    score = serializers.IntegerField()
    teacher_id = serializers.CharField()
    task_check = serializers.BooleanField()
    task_group = serializers.JSONField()
    task_student = serializers.JSONField()
    attempts = serializers.IntegerField()

    # class Meta:
    #     model = Task
    #     fields = ['id','topic_id_task','name','comment','start_date','end_date','task_id_type','score','teacher_id']

    def validate(self, data):
        current_datetime = timezone.now()
        name = data.get('name', None)
        comment = data.get('comment', None)
        topic_id_task = data.get('topic_id_task', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        score = data.get('score', None)
        teacher_id = data.get('teacher_id', None)
        task_check = data.get('task_check', None)
        task_group = data.get('task_group', None)
        task_student = data.get('task_student', None)
        attempts = data.get('attempts', None)
        # print(type(task_check))
        if name is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq nomini kiritish majburiy..."
                }
            )
        if task_group is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Guruhlar topilmadi va kiritish majburiy..."
                }
            )
        if not task_check:
            if not task_group:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        "message": "Guruhlar topilmadi va kiritish majburiy..."
                    }
                )
        else:
            if not task_student:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        "message": "Talabalar topilmadi va kiritish majburiy..."
                    }
                )

        if comment is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq uchun izoh kiritish majburiy..."
                }
            )
        if task_check is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Taba kesmidagi qiymatlar guruh va talablar olish task_check kirtilishi zarur..."
                }
            )
        if topic_id_task is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzuvga birktrilganligi kiritish majburiy..."
                }
            )
        if score is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq ballari kiritish majburiy..."
                }
            )
        if int(score) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan qiymay manfi, faqat musbat qabul qiladi."
                }
            )
        if teacher_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqga birktrilgan o`qtuvchi kiritish majburiy..."
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
        if attempts is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqga urinishlar kiritish majburiy..."
                }
            )
        return data


class Task_GroupsSerializers(serializers.Serializer):
    task_group_id = serializers.UUIDField()

    def validate(self, data):
        task_group_id = data.get('task_group_id', None)
        if task_group_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq fayl nomini kiritish majburiy..."
                }
            )

        return data


class Task_fileSerializers(serializers.Serializer):
    task_file = serializers.FileField()
    task = serializers.UUIDField()

    class Meta:
        model = Task_file
        fields = ['task_file', 'task']

    def validate(self, data):
        task_file = data.get('task_file', None)
        if task_file is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq faylini kiritish  majburiy..."
                }
            )
        return data


class ViewOneGroup(serializers.ModelSerializer):
    specialty = TaskbspecialitySerializer(read_only=True, many=False)
    group_curriculum = TaskCurriculumSerializer(read_only=True, many=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'h_id', 'specialty', 'group_curriculum']


class ViewOneStudent(serializers.ModelSerializer):
    group = ConnectGroupSerializers(read_only=True, many=False)

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'group']


class ViewOneTask_students(serializers.ModelSerializer):
    task_group_id = ViewOneGroup(many=False, read_only=True)
    task_student_id = ViewOneStudent(many=False, read_only=True)

    class Meta:
        model = Task_students
        fields = ['id', 'task_check', 'task_group_id', 'task_student_id']


class ViewOneTask(serializers.ModelSerializer):
    task_students = ViewOneTask_students(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'topic_id_task', 'name', 'comment', 'start_date', 'end_date', 'task_id_type', 'score',
                  'attempts', 'task_students']


class UpdateTask(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=250)
    comment = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    score = serializers.IntegerField()
    attempts = serializers.IntegerField()
    task_group = serializers.JSONField()
    task_student = serializers.JSONField()

    def validate(self, data):
        current_datetime = timezone.now()
        name = data.get('name', None)
        comment = data.get('comment', None)
        topic_id_task = data.get('topic_id_task', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        task_id_type = data.get('topic_id_task', None)
        score = data.get('score', None)
        teacher_id = data.get('teacher_id', None)
        task_check = data.get('task_check', None)
        task_group = data.get('task_group', None)
        task_student = data.get('task_student', None)
        attempts = data.get('attempts', None)
        # print(type(task_check))
        if name is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq nomini kiritish majburiy..."
                }
            )
        if task_group is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Guruhlar topilmadi va kiritish majburiy..."
                }
            )
        if not task_check:
            if not task_group:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        "message": "Guruhlar topilmadi va kiritish majburiy..."
                    }
                )
        else:
            if not task_student:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        "message": "Talabalar topilmadi va kiritish majburiy..."
                    }
                )

        if comment is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq uchun izoh kiritish majburiy..."
                }
            )
        if task_check is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Taba kesmidagi qiymatlar guruh va talablar olish task_check kirtilishi zarur..."
                }
            )
        if topic_id_task is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzuvga birktrilganligi kiritish majburiy..."
                }
            )
        if task_id_type is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq shakli kiritish majburiy..."
                }
            )
        if score is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq ballari kiritish majburiy..."
                }
            )
        if int(score) <= 0:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Kirtilgan qiymay manfi, faqat musbat qabul qiladi."
                }
            )
        if teacher_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqga birktrilgan o`qtuvchi kiritish majburiy..."
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
        if attempts is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriqga urinishlar kiritish majburiy..."
                }
            )
        return data


class Task_fileUpdateSerializers(serializers.Serializer):
    task_file = serializers.FileField()
    task = serializers.UUIDField()
    task_file_id = serializers.UUIDField()

    class Meta:
        model = Task_file
        fields = [ 'task_file_id','task_file', 'task']

    def validate(self, data):
        task_file = data.get('task_file', None)
        task_file_id = data.get('task_file_id', None)
        if task_file is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq faylini kiritish  majburiy..."
                }
            )
        if task_file_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq id bilan kiritish  majburiy..."
                }
            )
        return data
