from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from content.models import Task, Task_students, Task_file, Student_file, Topic, LessonRoom, Content_teacher, Content
from subjects.models import Subject


class TopicSerializers(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'in_progress', 'content_teacher_connect', 'content_id_topic', 'teacher_id',
                  'topic_bigbluebutton']


class TasksfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = Task_file
        fields = ['task_file']


def validate_file_size(value):
    # Set your desired maximum file size in bytes
    max_size = 5242880  # 10MB in bytes

    if value.size > max_size:
        raise serializers.ValidationError({
            'status': False,
            'message': 'File hajmi 5MB oshishi kerak emas!'
        })


class TaskSerializers(serializers.ModelSerializer):
    task_files = TasksfileSerializers(read_only=True, many=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'name',
            'comment',
            'start_date',
            'end_date',
            'score',
            'task_files',
            'attempts'
        ]


class Student_fileSerializers(serializers.ModelSerializer):
    class Meta:
        model = Student_file
        fields = ['id', 'number', 'student_file', 'file_date_sending', 'comment']


class Task_studentsSerializers(serializers.ModelSerializer):
    tasks_id = TaskSerializers(read_only=True, many=False)
    student_task_fayls = Student_fileSerializers(read_only=True, many=True)

    class Meta:
        model = Task_students
        fields = [
            'id',
            'tasks_id',
            'mark',
            'student_task_fayls',
            'status_control',
            'time_status',
            'is_status',
            'uploading_file_status',
            'number',
            'is_passed',
            'number_status'
        ]


class TasktakeSerializers(serializers.Serializer):
    student_id = serializers.UUIDField()
    student_file = serializers.FileField(validators=[validate_file_size])
    tasks_id = serializers.UUIDField()
    student_connect_task_id = serializers.UUIDField()
    comment = serializers.CharField(default=None, required=False)

    def validate(self, data):
        student_id = data.get('student_id', None)
        student_file = data.get('student_file', None)
        tasks_id = data.get('tasks_id', None)
        student_connect_task_id = data.get('student_connect_task_id', None)
        comment = data.get('comment', None)
        if student_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Student kiritish majburiy..."
                }
            )
        if student_file is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq fayili kiritish majburiy..."
                }
            )
        if tasks_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Topshiriq kiritish majburiy..."
                }
            )
        if student_connect_task_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Student va topshiriq boglanishi kiritish majburiy..."
                }
            )

        return data


class Subject_Name_Serialzier(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name', 'code']


class Content_List_Serializer(serializers.ModelSerializer):
    subject_id = Subject_Name_Serialzier()

    class Meta:
        model = Content
        fields = ['subject_id']


class Content_teacher_list_Serializer(serializers.ModelSerializer):
    content_id = Content_List_Serializer()

    class Meta:
        model = Content_teacher
        fields = [
            'content_id'
        ]


class LessonRoom_list_Serializer(serializers.ModelSerializer):
    connect = Content_teacher_list_Serializer(many=True)

    class Meta:
        model = LessonRoom
        fields = ['id', 'name', 'team_bigbluebutton', 'teacher_id', 'connect','start_datetime']
