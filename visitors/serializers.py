from rest_framework import serializers
from bigbluebutton.models import Bigbluebutton_Model
from content.models import Topic, LessonRoom, Content_teacher, Content, Video_content, File_content
from employee.models import Employee


class LessonRoomSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()

    class Meta:
        model = LessonRoom
        fields = ['id', 'name', 'connect', 'teacher', 'groups', 'subject', 'education']

    def get_teacher(self, obj):
        return obj.teacher_id.full_name

    def get_education(self, obj):

        edu_type = []
        for item in obj.connect.all():
            gitem = {}
            gitem['curriculum'] = item.content_id.curriculum_id.name
            gitem['edu_type'] = item.content_id.curriculum_id.educationform.name
            edu_type.append(gitem)
        return edu_type

    def get_groups(self, obj):
        group = []
        for item in obj.connect.all():
            gtitem = []
            for g in item.group_by.all():
                gitem = {}
                gitem['id'] = g.id
                gitem['name'] = g.name
                gtitem.append(gitem)
            group.append(gitem)
        return group

    def get_subject(self, obj):
        subjects = []
        for item in obj.connect.all():
            d = {}
            d['id'] = item.content_id.subject_id.id
            d['name'] = item.content_id.subject_id.name
            subjects.append(d)
        return subjects


class TopicSerializeInfoSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['id', 'name', 'subject', 'teacher', 'education', 'groups']

    def get_teacher(self, obj):
        return obj.content_teacher_connect.teacher_id.full_name

    def get_groups(self, obj):
        gtitem = []
        for group in obj.content_teacher_connect.group_by.all():  # Access groups through group_by ManyToManyField
            gitem = {
                'id': group.id,
                'name': group.name
            }
            gtitem.append(gitem)
        return gtitem

    def get_subject(self, obj):
        return obj.content_id_topic.subject_id.name

    def get_education(self, obj):
        gitem = {}
        gitem['curriculum'] = obj.content_id_topic.curriculum_id.name
        gitem['edu_type'] = obj.content_id_topic.curriculum_id.educationform.name

        return gitem


class BigBlubuttonSerializer(serializers.ModelSerializer):

    patok_is = serializers.SerializerMethodField()
    hisob = serializers.SerializerMethodField()
    class Meta:
        model = Bigbluebutton_Model
        fields = [
            'id', 'name', 'patok_is','status','hisob'
        ]

    def get_patok_is(self, obj):
        check = False
        if obj.topic_id is None:
            check = True
        return check
    def get_hisob(self, obj):
        if obj.topic_id is None:
            # Serialize the team_id data if topic_id is None
            team_data = LessonRoomSerializer(obj.team_id, many=False).data
            return team_data
        else:
            # Serialize the topic_id data otherwise
            topic_data = TopicSerializeInfoSerializer(obj.topic_id, many=False).data
            return topic_data


class CTecherListAll_Serializer(serializers.ModelSerializer):
    teacher_fio = serializers.SerializerMethodField()

    class Meta:
        model = Content_teacher
        fields = [
            'id', 'teacher_id', 'teacher_fio',
        ]

    def get_teacher_fio(self, obj):
        return obj.teacher_id.full_name


class Content_teacherlistSerailer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    file_count = serializers.SerializerMethodField()
    video_count = serializers.SerializerMethodField()
    title_count = serializers.SerializerMethodField()

    class Meta:
        model = Content_teacher
        fields = [
            'id', 'subject', 'groups', 'title_count', 'file_count', 'video_count'
        ]

    def get_subject(self, obj):
        return obj.content_id.subject_id.name

    def get_groups(self, obj):
        g_dic = []
        for item in obj.group_by.all():
            g_dic.append(item.name)
        return g_dic

    def get_file_count(self, obj):
        try:
            all_item = obj.content_teacher_connect.all()
            summ = 0
            for item in all_item:
                summ += item.topic_files.all().count()
            return summ
        except Exception as ex:
            return 0

    def get_video_count(self, obj):
        try:
            all_item = obj.content_teacher_connect.all()
            summ = 0
            for item in all_item:
                summ += item.topic_videos.all().count()
            return summ
        except Exception as ex:
            return 0

    def get_title_count(self, obj):
        try:
            all_item = obj.content_teacher_connect.all().count()
            return all_item
        except Exception as ex:
            return 0


class Topic_Video_list_Seralizer(serializers.ModelSerializer):
    file = serializers.FileField(source='vide_file')

    class Meta:
        model = Video_content
        fields = [
            'id', 'name', 'file', 'created_at'
        ]


class Topic_File_list_Seralizer(serializers.ModelSerializer):
    file = serializers.FileField(source='file_file')

    class Meta:
        model = File_content
        fields = [
            'id', 'name', 'file', 'created_at'
        ]

    def get_file(self, obj):
        return obj.file_file


class Topic_list_Seralizer(serializers.ModelSerializer):
    topic_videos = Topic_Video_list_Seralizer(many=True)
    topic_files = Topic_File_list_Seralizer(many=True)

    class Meta:
        model = Topic
        fields = [
            'id', 'number', 'name', 'in_progress', 'topic_videos', 'topic_files', 'created_at'
        ]
