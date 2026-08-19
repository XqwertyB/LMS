from rest_framework import serializers
from .models import Content, Roletype, Content_teacher, Topic, Video_content, File_content, Task_type, Task
from subjects.serializers import SubjectSerializer
from learning_process.serializers import CurriculumSerializer, EducationlangSerializer
from semestr.serializers import HsemesterSerializer
from employee.serializers import TeacherSerializer
from group.serializers import GroupSerializer, Group
from rest_framework.exceptions import ValidationError
from bigbluebutton.serializers import Bigbluebutton_ModelSerializer
from employee.models import Employee
from shared.models import TrainingType


class GroupContentSerializerInfo(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'faculty', 'educationLang'
        ]


class TrainingTypeSeralizerInfo(serializers.ModelSerializer):
    class Meta:
        model = TrainingType
        fields = [
            'id', 'name', 'code'
        ]


class TeacherSeralizerInfo(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'employee_id_number'
        ]


class Connect_TeacherSerializerInfo(serializers.ModelSerializer):
    teacher_id = TeacherSeralizerInfo(many=False, read_only=True)
    group_lang = EducationlangSerializer(many=False, read_only=True)
    group_by = GroupContentSerializerInfo(many=True, read_only=True)
    training_type = TrainingTypeSeralizerInfo(many=False, read_only=True)

    class Meta:
        model = Content_teacher
        fields = [
            'id', 'teacher_id', 'group_lang', 'group_by', 'training_type', 'content_id'
        ]


# from group

class ContentViewSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()
    curriculum_name = serializers.SerializerMethodField()
    content_semestrs_name = serializers.SerializerMethodField()
    groups_obj = serializers.SerializerMethodField()
    educationtype = serializers.SerializerMethodField()
    educationform = serializers.SerializerMethodField()
    subjectgroup = serializers.SerializerMethodField()
    credit = serializers.SerializerMethodField()
    teacher_content = Connect_TeacherSerializerInfo(many=True, read_only=True)

    class Meta:
        model = Content
        fields = [
            'id', 'subject_name', 'curriculum_name', 'content_semestrs_name',
            'semestr_action', 'groups_obj', 'educationtype', 'educationform', 'subjectgroup', 'credit',
            'teacher_content'
        ]

    def get_subject_name(self, obj):
        return obj.subject_id.name

    def get_subjectgroup(self, obj):
        return obj.subject_id.subjectgroup.name

    def get_credit(self, obj):
        return obj.credit

    def get_curriculum_name(self, obj):
        return obj.curriculum_id.name

    def get_educationtype(self, obj):
        return obj.curriculum_id.educationtype.name

    def get_educationform(self, obj):
        return obj.curriculum_id.educationform.name

    def get_content_semestrs_name(self, obj):
        return obj.content_semestrs.name

    def get_groups_obj(self, obj):
        group_list = []
        for group in obj.group.all():
            one = {}
            one['id'] = group.id
            one['name'] = group.name
            lang = {}
            lang['id'] = group.educationLang.id
            lang['name'] = group.educationLang.name
            one['lang'] = lang
            group_list.append(one)
        return group_list


class RoletypeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roletype
        fields = '__all__'


class RoletypeCreateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs

    class Meta:
        model = Roletype
        fields = '__all__'


class Content_teacherViewSerializer(serializers.ModelSerializer):
    content_id = ContentViewSerializer(many=False, read_only=True)
    teacher_id = TeacherSerializer(many=False, read_only=True)
    roletype_id_teacher = RoletypeViewSerializer(many=False, read_only=True)
    group_lang = EducationlangSerializer(many=False, read_only=True)
    group_by = GroupSerializer(many=True, read_only=True)
    training_type = TrainingTypeSeralizerInfo(many=False, read_only=True)

    class Meta:
        model = Content_teacher
        fields = '__all__'


class Content_teacherCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if not attrs.get('teacher_id'):
            data = {'teacher_id': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('content_id'):
            data = {'content_id': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('group_lang'):
            data = {'group_lang': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('group_by'):
            data = {'group_by': "Bo`sh qiymat!"}
            raise ValidationError(data)
        if not attrs.get('training_type'):
            data = {'training_type': "Bo`sh qiymat!"}
        else:
            return attrs

    class Meta:
        model = Content_teacher
        fields = '__all__'

    def create(self, validated_data):
        content_id = validated_data.get('content_id')
        group_by = validated_data.get('group_by')
        teacher_id = validated_data.get('teacher_id')
        group_lang = validated_data.get('group_lang')
        training_type = validated_data.get('training_type')
        # You can customize the behavior before saving the instance
        # For example, adding additional fields, modifying data, etc.
        instance = Content_teacher()
        instance.teacher_id = teacher_id
        instance.content_id = content_id
        instance.group_lang = group_lang
        instance.training_type = training_type
        instance.totatl_score_jn = content_id.totatl_score_jn
        instance.totatl_score_on = content_id.totatl_score_on
        instance.totatl_score_yn = content_id.totatl_score_yn
        instance.save()
        # Perform any additional operations if needed
        for group in group_by:
            instance.group_by.add(group)
        instance.save()
        return instance


class TopicViewSerializer(serializers.ModelSerializer):
    # topic_bigbluebutton = serializers.UUIDField(required=False,read_only=True)
    count_tasks = serializers.SerializerMethodField()

    def get_count_tasks(self, obj):
        return obj.topic_set_task.count()

    class Meta:
        model = Topic
        fields = ['id', 'name', 'number', 'in_progress', 'content_teacher_connect', 'content_id_topic', 'teacher_id',
                  'topic_bigbluebutton', 'count_tasks']


class TopicCreateSerializer(serializers.ModelSerializer):
    topic_bigbluebutton = serializers.UUIDField(required=False, read_only=True)

    def validate(self, data):
        name = data.get('name', None)
        content_teacher_connect = data.get('content_teacher_connect', None)
        content_id_topic = data.get('content_id_topic', None)
        teacher_id = data.get('teacher_id', None)

        if name is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzuni nomini kirtilishi majburiy ..."
                }
            )
        if content_teacher_connect is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzular id kirtilishi majburiy..."
                }
            )
        if content_id_topic is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzular id kirtilishi majburiy..."
                }
            )
        if teacher_id is None:
            raise serializers.ValidationError(
                {
                    'status': False,
                    "message": "Mavzular id kirtilishi majburiy..."
                }
            )

        return data

    class Meta:
        model = Topic
        fields = ['id', 'name', 'number', 'in_progress', 'content_teacher_connect', 'content_id_topic', 'teacher_id',
                  'topic_bigbluebutton']

    def create(self, validated_data):
        name = validated_data.get('name')
        content_teacher_connect = validated_data.get('content_teacher_connect')
        content_id_topic = validated_data.get('content_id_topic')
        teacher_id = validated_data.get('teacher_id')
        instance = Topic()
        topics = Topic.objects.filter(content_id_topic=content_id_topic,
                                      content_teacher_connect=content_teacher_connect).count()
        instance.name = name
        instance.content_teacher_connect = content_teacher_connect
        instance.content_id_topic = content_id_topic
        instance.teacher_id = teacher_id
        instance.number = topics + 1
        instance.save()
        return instance


class Video_contentViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video_content
        fields = '__all__'


class File_contentViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = File_content
        fields = '__all__'


class Task_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task_type
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class Task_typeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task_type
        fields = ['id', 'name', 'code']


class Task_typeCreateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if not attrs.get('name'):
            data = {'name': "Bo`sh qiymat!"}
            raise ValidationError(data)
        elif not attrs.get('code'):
            data = {'code': "Bo`sh qiymat!"}
            raise ValidationError(data)
        else:
            return attrs

    class Meta:
        model = Task_type
        fields = ['id', 'name', 'code']


class Content_countSerializer(serializers.Serializer):
    maruza = serializers.IntegerField()
    video = serializers.IntegerField()
    topshiriq = serializers.IntegerField()


class Content_teacherSerializerdetect_subject(serializers.ModelSerializer):
    teacher_id = TeacherSeralizerInfo(many=False, read_only=True)
    group_lang = EducationlangSerializer(many=False, read_only=True)
    group_by = GroupSerializer(many=True, read_only=True)
    training_type = TrainingTypeSeralizerInfo(many=False, read_only=True)

    class Meta:
        model = Content_teacher
        fields = [
            'id', 'content_id', 'group_lang', 'group_by', 'teacher_id', 'training_type'
        ]


class Content_teacherSerializerUpdate(serializers.ModelSerializer):
    group_by = serializers.ListSerializer(child=serializers.UUIDField())  # List of group UUIDs from frontend
    training_type = serializers.UUIDField()  # UUID for training_type from frontend

    class Meta:
        model = Content_teacher
        fields = [
            'id', 'group_by', 'training_type'
        ]

    def update(self, instance, validated_data):
        # Olingan ma'lumotlardan `group_by`ni olib tashlash
        group_by_data = validated_data.pop('group_by', None)
        training_type_uuid = validated_data.get('training_type', None)

        # `training_type`ni UUID orqali haqiqiy obyektga o'zgartirish
        if training_type_uuid:
            try:
                training_type = TrainingType.objects.get(id=training_type_uuid)
                instance.training_type = training_type
            except TrainingType.DoesNotExist:
                raise serializers.ValidationError({"training_type": "Bu training_type mavjud emas!"})

        # `group_by`ni yangilash (agar yangi ro'yxat bo'lsa)
        if group_by_data:
            # Guruh UUID'larni haqiqiy `Group` obyektlariga aylantirish
            try:
                groups = Group.objects.filter(id__in=group_by_data)
                if len(groups) != len(group_by_data):
                    raise serializers.ValidationError({"group_by": "Ba'zi guruhlar topilmadi!"})
                instance.group_by.set(groups)  # Guruhlarni yangilash
            except Group.DoesNotExist:
                raise serializers.ValidationError({"group_by": "Ba'zi guruhlar mavjud emas!"})

        instance.save()  # Yangilangan instance'ni saqlash

        return instance
