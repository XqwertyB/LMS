from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from config.permissions import AllowOnlyTrustedOrigins
from learning_process.models import Curriculum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
import datetime
from rest_framework.exceptions import ValidationError
from employee.models import Employee
from content.models import Content, Content_teacher, Topic, Video_content, File_content, Content_teacher, Task, \
    Task_students, Task_file, LessonRoom
from content.serializers import (
    ContentViewSerializer, RoletypeViewSerializer, Content_teacherViewSerializer,
    TopicViewSerializer, TopicCreateSerializer
)
from shared.permissions import IsTeacher, IsAdminOrTeacher
from .serializers import (Teacher_TopicSerializers, OwenVideAddSerializers, Taskcreatewithfile, GetScorelimitSerailizer,
                          TaskFilecreateSerializer, TaskFilescreateschemaSerializer, TaskFileupdateSerializer,
                          Teacher_VideoCreateSerializers, Teacher_VideoSerializers, OwenFileAddSerializers,
                          Teacher_FileCreateSerializers, Teacher_File_contentSerializers,
                          BigbluebuttonCreateSerial, Task_mark_studentSerializer, Task_studentsSerializer,
                          TaskviewSerializer, TaskcreateSerializer, Task_file_add_sxemSerializer,
                          StudnetgetGorupingSerializer, GetScoreTopiclimitSerailizer,
                          Task_fileSerializer, TaskcreatesxemSerializer, TaskallsxemSerializer,
                          Task_groupSerializer, TaskgroupsxemSerializer, TaskactionSerializer, TaskFUpdateSerializer,
                          TaskstudentsxemSerializer, TaskStudentSerializer, TaskGorupAddSerializer,
                          LessonRoomListSerialzier, LessonRoomCreateSerialzer, Content_teacherList_Serializer,
                          RoomLessonUpdateSerializer)
from bigbluebutton.models import Bigbluebutton_Model, BigbluebuttonMain, Bigbluebutton_sub
from bigbluebutton.serializers import Bigbluebutton_ModelSerializer
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
import xmltodict
import urllib.parse
import requests
from bigbluebutton.checksum_genrate import checksum_genration
from students.models import Student
from django.utils import timezone
from group.models import Group
from .func_count import countremain, countremaintopic
import json
from django.db.models import Count, Q


def Check_teacher(teacher_id):
    try:
        teacher = Employee.objects.get(employee_id_number=teacher_id)

        return {'check': True, 'teacher': teacher}
    except Exception as ex:
        return {'check': False, 'message': str(ex)}


def Check_teacher_basic_id(teacher_id):
    try:
        teacher = Employee.objects.get(id=teacher_id)

        return {'check': True, 'teacher': teacher}
    except Exception as ex:
        return {'check': False}


def Teacher_id_get(teacher_id):
    try:
        teacher = Employee.objects.get(hemis_id=teacher_id)
        # print(teacher)
        return {'check': True, 'teacher': teacher.id}
    except Exception as ex:
        return {'check': False}


class Teacher_get_basic_id(APIView):

    def post(self, request, format=None):
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'error': True, 'message': 'teacher_id yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_400_BAD_REQUEST)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            return Response({'succes': True, 'teacher': teacher['teacher']}, status=status.HTTP_200_OK)
        else:
            return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Teacher_Contents_get(APIView):
    permission_classes = (AllowOnlyTrustedOrigins,IsTeacher, IsAuthenticated,)

    def post(self, request, format=None):
        curriculum_id = request.data.get('curriculum_id')
        active = request.data.get('active')
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'})
        if curriculum_id is None:
            return Response({'errors': 'curriculum_id yuborilgan jsonda  mavjud emas'})
        if active is None:
            return Response({'errors': 'active yuborilgan jsonda  mavjud emas'})
        teacher = Check_teacher(teacher_id)
        try:
            curriculum = Curriculum.objects.get(cur_id=curriculum_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)

        if teacher['check']:
            contents = Content_teacher.objects.filter(teacher_id=teacher['teacher'],
                                                      content_id__curriculum_id=curriculum,
                                                      content_id__semestr_action=active)
            serializer = Content_teacherViewSerializer(contents, many=True)

            return Response({'succes': True, 'result': serializer.data}, status=status.HTTP_200_OK)

        return Response({'succes': False, 'message': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Teacher_Content_get(APIView):  # oquv rejasiz
    permission_classes = (AllowOnlyTrustedOrigins,IsTeacher,)

    def post(self, request, format=None):
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'error': True, 'message': 'teacher_id yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_404_NOT_FOUND)

        teacher = Check_teacher(teacher_id)

        if teacher['check']:
            contents = Content_teacher.objects.filter(teacher_id=teacher['teacher'],content_id__semestr_action=True)
            for i in contents:

                maruzalar = Topic.objects.filter(content_teacher_connect=i, status_action=True)
                maruza_cunt = maruzalar.count()
                # print(maruza_cunt)
                video_count = 0
                task_count = 0
                for j in maruzalar:
                    video_content = Video_content.objects.filter(video_id_topic=j).count()
                    video_count += video_content
                    task_content = Task.objects.filter(topic_id_task=j).count()
                    task_count += task_content
                try:
                    i.task_count = task_count
                    i.video_count = video_count
                    i.topic_count = maruza_cunt
                    i.save()

                except Exception as e:
                    return Response({'errors': True, 'teacher_status': str(e)},
                                    status=status.HTTP_400_BAD_REQUEST)

            serializer = Content_teacherViewSerializer(contents, many=True)

            return Response({'succes': True, 'result': serializer.data}, status=status.HTTP_200_OK)

        return Response({'errors': True, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Teacher_View_Topic(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher,]
    def post(self, request, format=None):
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        content_id_topic = request.data.get('content_id_topic')
        if content_id_topic is None:
            return Response({'errors': 'content_id_topic yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_404_NOT_FOUND)
        content_teacher_connect = request.data.get('content_teacher_connect')
        if content_teacher_connect is None:
            return Response({'errors': 'content_teacher_connect yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        try:
            content = Content.objects.get(id=content_id_topic)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            connect = Content_teacher.objects.get(id=content_teacher_connect)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        if teacher['check']:
            contents = Topic.objects.filter(content_teacher_connect=connect, content_id_topic=content,
                                            teacher_id=teacher['teacher']).order_by('number')
            serializer = TopicViewSerializer(contents, many=True)
            return Response({'succes': True, 'result': serializer.data}, status=status.HTTP_200_OK)

        return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Teacher_Active_Topic(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsTeacher, ]
    def post(self, request, format=None):
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'error': True, 'message': 'teacher_id yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_404_NOT_FOUND)
        content_id_topic = request.data.get('content_id_topic')
        if content_id_topic is None:
            return Response({'error': True, 'message': 'content_id_topic yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_404_NOT_FOUND)
        topic_id = request.data.get('topic_id')
        if topic_id is None:
            return Response({'error': True, 'message': 'topic_id yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_404_NOT_FOUND)
        content_teacher_connect = request.data.get('content_teacher_connect')
        if content_teacher_connect is None:
            return Response({'error': True, 'message': 'content_teacher_connect yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        try:
            content = Content.objects.get(id=content_id_topic)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            connect = Content_teacher.objects.get(id=content_teacher_connect)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        if teacher['check']:
            if Topic.objects.filter(content_teacher_connect=connect, content_id_topic=content,
                                    teacher_id=teacher['teacher']).exists():
                try:
                    topic = Topic.objects.get(id=topic_id)
                    topics = Topic.objects.filter(content_id_topic=content, teacher_id=teacher['teacher'])
                    for item in topics:
                        item.in_progress = False
                        item.save()
                    topic.in_progress = True
                    topic.save()
                    return Response({'succes': True}, status=status.HTTP_201_CREATED)
                except Exception as ex:
                    return Response(
                        {'error': True, 'message': "Shu fanga biriktirilgan mavzu topilmadi!"},
                        status=status.HTTP_400_BAD_REQUEST)

            return Response({'error': True, 'message': 'Shu fanga biriktirilgan mavzu topilmadi!'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Teacher_Add_Topic(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsTeacher, ]
    def post(self, request, format=None):
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'error': True, 'message': 'teacher_id yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_403_FORBIDDEN)
        content_id_topic = request.data.get('content_id_topic')
        if content_id_topic is None:
            return Response({'error': True, 'message': 'content_id_topic yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_403_FORBIDDEN)
        name = request.data.get('name')
        if name is None:
            return Response({'error': True, 'message': 'name yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_403_FORBIDDEN)
        content_teacher_connect = request.data.get('content_teacher_connect')
        if content_teacher_connect is None:
            return Response({'error': True, 'message': 'content_teacher_connect yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_403_FORBIDDEN)
        teacher = Check_teacher(teacher_id)
        try:
            content = Content.objects.get(id=content_id_topic)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            connect = Content_teacher.objects.get(id=content_teacher_connect)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        if teacher['check']:
            request.data.update({'teacher_id': teacher['teacher'].id})
            serializer = TopicCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'success': True,
                     'result': serializer.data},
                    status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Teacher_change_Topic(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsTeacher, ]
    def get_object(self, pk):
        try:
            return Topic.objects.get(pk=pk)
        except Topic.DoesNotExist:
            return Response({'error': True, 'message': 'Mavzu topilmadi...'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        item = self.get_object(pk)
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'message': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_403_FORBIDDEN)
        name = request.data.get('name')
        if name is None:
            return Response({'message': 'name yuborilgan jsonda  mavjud emas'}, status=status.HTTP_403_FORBIDDEN)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                item.name = name
                item.save()
                serializer = TopicCreateSerializer(item, many=False)
                return Response({'success': True, 'rezults': serializer.data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Topic_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    # @swagger_auto_schema(request_body=Teacher_TopicSerializers)
    def get(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('topic_id')
        teacher_id = self.request.query_params.get('teacher_id')
        # connect_id = self.request.query_params.get('connect_id')
        if topic_id is None:
            return Response({'message': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'message': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        # if connect_id is None:
        #     return Response({'errors': 'connect_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)

        teacher = Check_teacher(teacher_id)
        try:
            item = Topic.objects.get(id=topic_id)
        except item.DoesNotExist:
            return Response({'error': True, 'message': 'Mavzu topilmadi...'},
                            status=status.HTTP_404_NOT_FOUND)
        if teacher['check']:
            obj = Teacher_TopicSerializers(item, many=False)
            return Response({
                'success': True,
                'result': obj.data
            }, status=status.HTTP_200_OK)
        return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Topic_Video_Add(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsTeacher,]
    @swagger_auto_schema(request_body=OwenVideAddSerializers)
    def post(self, request, *args, **kwargs):
        serializers = OwenVideAddSerializers(data=request.data)
        if serializers.is_valid():
            topic_id = serializers.validated_data['topic_id']
            teacher_id = serializers.validated_data['teacher_id']
            videos = serializers.validated_data['video']
            name = serializers.validated_data['name']
            if topic_id is None:
                return Response({'message': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
            if teacher_id is None:
                return Response({'message': 'teacher_id yuborilgan jsonda  mavjud emas'},
                                status=status.HTTP_404_NOT_FOUND)
            if videos is None:
                return Response({'message': 'videos yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
            if name is None:
                return Response({'message': 'name yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
            try:
                try:
                    item = Topic.objects.get(id=topic_id)
                except Topic.DoesNotExist:
                    return Response({'errors': True, 'massegs': 'Topic topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'succes': False, 'massege': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            teacher = Check_teacher(teacher_id)
            if teacher['check']:

                try:
                    video = Teacher_VideoCreateSerializers(
                        data={
                            'name': name,
                            'vide_file': videos,
                            'video_id_topic': topic_id,
                            'teacher_id': teacher['teacher'].id
                        }
                    )
                    if video.is_valid():
                        video.save()
                    else:
                        return Response({'succes': False, 'message': video.errors},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'succes': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                video_content = Video_content.objects.filter(teacher_id_id=teacher['teacher'].id,
                                                             video_id_topic_id=item.id)
                sdata = Teacher_VideoSerializers(video_content, many=True)
                return Response({'succes': True, 'message': 'Videolar yukanldi!',
                                 'result': sdata.data}, status=status.HTTP_200_OK)
            else:
                return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'succes': False, 'message': serializers.errors}, status=status.HTTP_400_BAD_REQUEST)


class Topic_Video_Delete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsTeacher, ]
    @swagger_auto_schema(request_body=OwenVideAddSerializers)
    def delete(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('topic_id')
        teacher_id = self.request.query_params.get('teacher_id')
        pk = self.request.query_params.get('pk')
        if topic_id is None:
            return Response({'message': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'message': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if pk is None:
            return Response({'message': 'pk yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        try:
            try:
                item = Topic.objects.get(id=topic_id)
            except Topic.DoesNotExist:
                return Response({'errors': True, 'message': 'Topic topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'succes': False, 'massege': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                obj = Video_content.objects.get(id=pk)
            except Video_content.DoesNotExist:
                return Response({'errors': True, 'massegs': 'Video topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
            obj.delete()
            video_content = Video_content.objects.filter(teacher_id_id=teacher['teacher'].id,
                                                         video_id_topic_id=item.id)
            sdata = Teacher_VideoSerializers(video_content, many=True)
            return Response({'succes': True, 'message': 'Video ochirildi!',
                             'result': sdata.data}, status=status.HTTP_200_OK)
        else:
            return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Topic_File_Add(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsTeacher, ]
    @swagger_auto_schema(request_body=OwenFileAddSerializers)
    def post(self, request, *args, **kwargs):
        serializers = OwenFileAddSerializers(data=request.data)
        if serializers.is_valid():
            topic_id = serializers.validated_data['topic_id']
            teacher_id = serializers.validated_data['teacher_id']
            files = serializers.validated_data['files']
            name = serializers.validated_data['name']
            if topic_id is None:
                return Response({'message': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
            if teacher_id is None:
                return Response({'message': 'teacher_id yuborilgan jsonda  mavjud emas'},
                                status=status.HTTP_404_NOT_FOUND)
            if files is None:
                return Response({'message': 'files yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
            if name is None:
                return Response({'message': 'name yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
            try:
                try:
                    item = Topic.objects.get(id=topic_id)
                except Topic.DoesNotExist:
                    return Response({'errors': True, 'massegs': 'Topic topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'succes': False, 'massege': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            teacher = Check_teacher(teacher_id)
            if teacher['check']:
                try:
                    bfile = Teacher_FileCreateSerializers(
                        data={
                            'name': name,
                            'file_file': files,
                            'file_id_topic': item.id,
                            'teacher_id': teacher['teacher'].id
                        }
                    )
                    if bfile.is_valid():
                        bfile.save()
                    else:
                        return Response({'succes': False, 'message': bfile.errors},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'succes': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                bfile_content = File_content.objects.filter(teacher_id_id=teacher['teacher'], file_id_topic_id=item)
                sdata = Teacher_File_contentSerializers(bfile_content, many=True)
                return Response({'succes': True, 'message': 'Fayllar yuklandi!',
                                 'result': sdata.data}, status=status.HTTP_200_OK)
            else:
                return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'succes': False, 'message': serializers.errors}, status=status.HTTP_400_BAD_REQUEST)


class Topic_File_Delete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsTeacher, ]
    def delete(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('topic_id')
        teacher_id = self.request.query_params.get('teacher_id')
        pk = self.request.query_params.get('pk')
        if topic_id is None:
            return Response({'errors': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if pk is None:
            return Response({'errors': 'pk yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        try:
            try:
                item = Topic.objects.get(id=topic_id)
            except Topic.DoesNotExist:
                return Response({'errors': True, 'massegs': 'Topic topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'succes': False, 'massege': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                obj = File_content.objects.get(id=pk)
            except File_content.DoesNotExist:
                return Response({'errors': True, 'massegs': 'FIle topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
            obj.delete()
            bfile_content = File_content.objects.filter(teacher_id_id=teacher['teacher'].id,
                                                        file_id_topic_id=item.id)
            sdata = Teacher_File_contentSerializers(bfile_content, many=True)
            return Response({'succes': True, 'message': 'Fayl ochirildi!',
                             'result': sdata.data}, status=status.HTTP_200_OK)
        else:
            return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Topic_bigbluebutton_view(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def get(self, request, pk):
        # Handle GET request
        bbb = pk
        topic_id = self.request.query_params.get('topic_id')
        teacher_id = self.request.query_params.get('teacher_id')
        if topic_id is None:
            return Response({'errors': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            data = {'succes': False, 'message': 'Mavzu topilmadi!'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                obj = Bigbluebutton_Model.objects.get(id=bbb)
                serializer = Bigbluebutton_ModelSerializer(obj, many=False)
                data = {'succes': True, 'results': serializer.data}
                return Response(data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'errors': True, 'message': 'Bigbluebutton xonasi topilmadi'},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            data = {'succes': False, 'message': 'O`qtuvchi topilmadi!'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class Topic_bigbluebutton_create(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def post(self, request):
        serializer = BigbluebuttonCreateSerial(data=request.data)
        if serializer.is_valid():
            try:
                item = Topic.objects.get(id=serializer.data['topic_id'])
            except Topic.DoesNotExist:
                return Response({'errors': True, 'massegs': 'Mavzu topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
            teacher = Check_teacher(serializer.data['teacher_id'])
            if teacher['check']:
                with transaction.atomic():
                    try:
                        my_model = Bigbluebutton_Model()
                        my_model.name = serializer.validated_data['name']
                        if 'maxParticipants' in serializer.validated_data:
                            my_model.maxParticipants = serializer.validated_data['maxParticipants']
                        if 'duration' in serializer.validated_data:
                            my_model.duration = serializer.validated_data['duration']
                        my_model.add_random_field()
                        my_model.topic_id = item
                        my_model.save()
                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response({"success": False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    # print(my_model.id)
                    try:
                        base_url = BigbluebuttonMain.objects.last()
                        "URl qaytarish qo`shiladigan hona uchun mentor uchun "
                    except:
                        transaction.set_rollback(True)
                        data = {'success': False, 'message': 'Bigbluebutton base_url malumotlar omboridan topilmadi'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    try:
                        send_url = Bigbluebutton_sub.objects.get(uniq_id=1)
                        "URl qaytarish qo`shiladigan hona uchun mentor uchun "

                    except:
                        transaction.set_rollback(True)
                        data = {'success': False,
                                'message': 'Bigbluebutton send_url metod malumotlar omboridan topilmadi'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    try:
                        if not my_model.status:
                            fields_and_values = my_model.__dict__
                            query = ""
                            for index, (field_name, field_value) in enumerate(sorted(fields_and_values.items())):
                                if field_name not in ['id', 'created_at', 'updated_at', 'status_action', '_state']:
                                    if field_value:
                                        if index == len(fields_and_values) - 1:
                                            if field_name in ['name']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            elif field_name in ['attendeePW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            elif field_name in ['moderatorPW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            elif field_name in ['welcome']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            else:
                                                if type(field_value) == bool:
                                                    query += field_name + '=' + str(field_value).lower()
                                                else:
                                                    query += field_name + '=' + str(field_value)
                                        else:
                                            if field_name in ['name']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            elif field_name in ['attendeePW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            elif field_name in ['moderatorPW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            elif field_name in ['welcome']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            else:
                                                if type(field_value) == bool:
                                                    query += field_name + '=' + str(field_value).lower() + '&'
                                                else:
                                                    query += field_name + '=' + str(field_value) + '&'
                            xquery = send_url.url_method + query
                            checksum = checksum_genration(xquery, base_url.sicret_key)
                            url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
                            response = requests.get(url)
                            if response.status_code == 200:
                                parsed_dict = xmltodict.parse(response.text)
                                if parsed_dict['response']['returncode'] == 'SUCCESS':
                                    my_model.status = True
                                    my_model.redirect = True
                                    my_model.save()
                                else:
                                    my_model.status = False
                                    my_model.redirect = True
                                    my_model.save()
                                return Response({'success': True, 'results': parsed_dict['response']},
                                                status=status.HTTP_201_CREATED)
                            else:
                                transaction.set_rollback(True)
                                return Response({'success': False, 'message': 'bigbluebutton javob notogri'},
                                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            transaction.set_rollback(True)
                            return Response({'success': False, 'message': 'bigbluebutton xona ochilgan'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response({'succes': False, 'message': str(e)},
                                        status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Task_list_students(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def get(self, request):
        teacher_id = self.request.query_params.get('teacher_id')
        task_id = self.request.query_params.get('task_id')
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if task_id is None:
            return Response({'errors': 'task_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)

        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                task = Task.objects.get(id=task_id)
            except Exception as e:
                return Response({'succes': False, 'message': str(e)},
                                status=status.HTTP_404_NOT_FOUND)
            try:
                tasks = Group.objects.filter(task_group_list__tasks_id=task).distinct()
                serializers = StudnetgetGorupingSerializer(tasks, many=True)
                return Response({'succes': True, 'results': serializers.data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'succes': False, 'message': str(e)},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Task_student_mark(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def post(self, request):
        answare = Task_mark_studentSerializer(data=request.data)
        if answare.is_valid():
            try:
                student = Student.objects.get(id=answare.validated_data['student_id'])
            except Exception as e:
                return Response({'succes': False, 'massage': str(e)}, status=status.HTTP_404_NOT_FOUND)

            teacher = Check_teacher(answare.validated_data['teacher_id'])
            if teacher['check']:
                try:
                    task = Task.objects.get(id=answare.validated_data['task_id'])
                except Exception as e:
                    return Response({'succes': False, 'massage': str(e)}, status=status.HTTP_404_NOT_FOUND)
                try:
                    task_student = Task_students.objects.get(id=answare.validated_data['task_student_id'])
                except Exception as e:
                    return Response({'succes': False, 'massage': str(e)}, status=status.HTTP_404_NOT_FOUND)
                with transaction.atomic():
                    if task_student.tasks_id != task:
                        transaction.set_rollback(True)
                        return Response({'succes': False, 'massage': 'topshirga student boglanish xato!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if task_student.task_student_id != student:
                        transaction.set_rollback(True)
                        return Response({'succes': False, 'massage': 'studentga topshriq boglanish xato!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    mark = answare.validated_data['mark']
                    if task.score < mark:
                        transaction.set_rollback(True)
                        return Response(
                            {'succes': False, 'massage': 'Qo`yilgan baho topshiriq uchun ajratilgan ball`dan yuqori!'},
                            status=status.HTTP_400_BAD_REQUEST)
                    if task_student.mark:
                        if task.score * 0.6 < task_student.mark:
                            transaction.set_rollback(True)
                            return Response(
                                {'succes': False,
                                 'massage': 'Qo`yilgan bahoni o`zgartrib bo`lmaydi!'},
                                status=status.HTTP_400_BAD_REQUEST)
                    if not task_student.uploading_file_status:
                        transaction.set_rollback(True)
                        return Response(
                            {'succes': False, 'massage': 'O`quvchi tarafdan fayl yuklanmagan!'},
                            status=status.HTTP_400_BAD_REQUEST)

                    if task_student.is_status == False:
                        transaction.set_rollback(True)
                        return Response(
                            {'succes': False, 'massage': 'O`quvchiga hali topshiriq ruhsat yo`q!'},
                            status=status.HTTP_400_BAD_REQUEST)
                    if task_student.checking_status:
                        transaction.set_rollback(True)
                        return Response(
                            {'succes': False, 'massage': 'Baholanish imkonyat tugagan!'},
                            status=status.HTTP_400_BAD_REQUEST)
                    try:
                        task_student.checker = teacher['teacher']
                        if task_student.is_status == True:
                            limit = task.score * 0.6
                            if limit <= mark:
                                task_student.is_passed = True
                        if task_student.is_passed:
                            count = task_student.number + 1

                            obj = Task_students.objects.filter(number__exact=count,
                                                               tasks_id__topic_id_task=task_student.tasks_id.topic_id_task,
                                                               task_student_id=student).exists()
                            # print(obj)
                            if obj:
                                obj_x = Task_students.objects.filter(number__exact=count,
                                                                     tasks_id__topic_id_task=task_student.tasks_id.topic_id_task,
                                                                     task_student_id=student).last()

                                obj_x = Task_students.objects.get(id=obj_x.id)
                                obj_x.is_status = True
                                obj_x.save()
                            else:
                                topic_number = task_student.tasks_id.topic_id_task.number + 1
                                obj_topic_check = Topic.objects.filter(number__exact=topic_number,
                                                                       content_teacher_connect=task_student.tasks_id.topic_id_task.content_teacher_connect).exists()
                                if obj_topic_check:
                                    topic_x = Topic.objects.filter(number__exact=topic_number,
                                                                   content_teacher_connect=task_student.tasks_id.topic_id_task.content_teacher_connect).last()
                                    # print(topic_x)
                                    tasks_x = topic_x.topic_set_task.all()
                                    for tat in tasks_x:
                                        find = tat.task_students.filter(task_student_id=student, number__exact=1).last()
                                        if find:
                                            find.is_status = True
                                            find.save()
                                    # print(uitme)

                        task_student.mark = mark
                        task_student.mark_status = True
                        current_datetime = timezone.now()
                        task_student.mark_date = current_datetime
                        task_student.comment = answare.validated_data['comment']
                        if task_student.student_task_fayls.all().count() == task_student.tasks_id.attempts:
                            task_student.checking_status = True
                        task_student.save()
                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response({'success': False, 'massage': str(e)},
                                        status=status.HTTP_400_BAD_REQUEST)
                    return Response({'success': True, 'resluts': 'Talaba baholandi'},
                                    status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'teacher_status': teacher['check']},
                                status=status.HTTP_404_NOT_FOUND)

        else:
            return Response(answare.errors, status=status.HTTP_400_BAD_REQUEST)


class Bigbluebutton_check_session(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def get(self, request, *args, **kwargs):
        bbb_id = self.request.query_params.get('bbb_id')
        if bbb_id is None:
            return Response({'success': False, 'message': 'Meeting mavjud emas.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            base_url = BigbluebuttonMain.objects.last()
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "
        except:
            data = {'success': False, 'message': 'Asosiy manzil malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            send_url = Bigbluebutton_sub.objects.get(uniq_id=5)
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "

        except:
            data = {'success': False, 'message': 'Asosiy manzil(send_url) metod malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            obj = Bigbluebutton_Model.objects.get(pk=bbb_id)
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "
        except:
            data = {'success': False, 'message': 'Meeting malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            query = ""
            # Print field names and their values
            meetingID = str(obj.meetingID)
            moderatorPW = urllib.parse.quote(str(obj.moderatorPW).encode("utf-8"))
            query += 'meetingID=' + meetingID + "&moderatorPW=" + moderatorPW
            xquery = send_url.url_method + query
            checksum = checksum_genration(xquery, base_url.sicret_key)
            # print(checksum)
            url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
            response = requests.get(url)
            if response.status_code == 200:
                parsed_dict = xmltodict.parse(response.text)
                check_falied = parsed_dict['response']['returncode']
                if check_falied == 'FAILED':
                    obj.status = False
                    obj.save()
                    return Response(
                        {'success': True, 'message': "Xona status faolmas bo`ldi", 'results': parsed_dict['response']},
                        status=status.HTTP_400_BAD_REQUEST)
                if not obj.status:
                    obj.status = True
                    obj.save()
                return Response(
                    {'success': True, 'message': "Xona status faolmas bo`ldi", 'results': parsed_dict['response']},
                    status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'Meeting server bilan aloqa mavjud emas.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Bigbluebutton_restart(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def post(self, request, pk):
        bbb_id = pk
        try:
            bbb = Bigbluebutton_Model.objects.get(id=bbb_id)
        except Exception as e:
            return Response({'errors': True, 'message': 'Meeting xonasi topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', None)
        maxParticipants = request.data.get('maxParticipants', None)
        topic_id = request.data.get('topic_id', None)
        teacher_id = request.data.get('teacher_id', None)
        if name is None:
            return Response({'errors': True, 'massegs': 'Name bo`sh bo`lish kerak emas!'},
                            status=status.HTTP_404_NOT_FOUND)
        if maxParticipants is None:
            return Response({'errors': True, 'massegs': 'maxParticipants bo`sh bo`lish kerak emas!'},
                            status=status.HTTP_404_NOT_FOUND)
        if topic_id is None:
            return Response({'errors': True, 'massegs': 'topic_id bo`sh bo`lish kerak emas!'},
                            status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'errors': True, 'massegs': 'teacher_id bo`sh bo`lish kerak emas!'},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            item = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({'errors': True, 'massegs': 'Topic topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            with transaction.atomic():
                try:
                    bbb.name = name
                    bbb.maxParticipants = maxParticipants
                    bbb.add_random_field()
                    bbb.save()
                except Exception as e:
                    transaction.set_rollback(True)
                    return Response({"success": False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                # print(my_model.id)
                try:
                    base_url = BigbluebuttonMain.objects.last()
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "
                except:
                    transaction.set_rollback(True)
                    data = {'success': False, 'message': 'Bigbluebutton base_url malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    send_url = Bigbluebutton_sub.objects.get(uniq_id=1)
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "
                except:
                    transaction.set_rollback(True)
                    data = {'success': False,
                            'message': 'Bigbluebutton send_url metod malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    if not bbb.status:
                        fields_and_values = bbb.__dict__
                        query = ""
                        for index, (field_name, field_value) in enumerate(sorted(fields_and_values.items())):
                            if field_name not in ['id', 'created_at', 'updated_at', 'status_action', '_state']:
                                if field_value:
                                    if index == len(fields_and_values) - 1:
                                        if field_name in ['name']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        elif field_name in ['attendeePW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        elif field_name in ['moderatorPW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        elif field_name in ['welcome']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        else:
                                            if type(field_value) == bool:
                                                query += field_name + '=' + str(field_value).lower()
                                            else:
                                                query += field_name + '=' + str(field_value)
                                    else:
                                        if field_name in ['name']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        elif field_name in ['attendeePW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        elif field_name in ['moderatorPW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        elif field_name in ['welcome']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        else:
                                            if type(field_value) == bool:
                                                query += field_name + '=' + str(field_value).lower() + '&'
                                            else:
                                                query += field_name + '=' + str(field_value) + '&'
                        xquery = send_url.url_method + query
                        checksum = checksum_genration(xquery, base_url.sicret_key)
                        url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
                        response = requests.get(url)
                        if response.status_code == 200:
                            parsed_dict = xmltodict.parse(response.text)
                            if parsed_dict['response']['returncode'] == 'SUCCESS':
                                bbb.status = True
                                bbb.redirect = True
                                bbb.save()
                            else:
                                bbb.status = False
                                bbb.redirect = True
                                bbb.save()
                            return Response({'success': True, 'results': parsed_dict['response']},
                                            status=status.HTTP_200_OK)
                        else:
                            transaction.set_rollback(True)
                            return Response({'success': False, 'message': 'bigbluebutton javob notogri'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        transaction.set_rollback(True)
                        return Response({'success': False, 'message': 'bigbluebutton xona ochilgan'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    transaction.set_rollback(True)
                    return Response({'succes': False, 'message': str(e)},
                                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class Bigbluebutton_check_session_restart(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def get(self, request):
        bbb_id = self.request.query_params.get('bbb_id')
        teacher_id = self.request.query_params.get('teacher_id')
        try:
            bbb = Bigbluebutton_Model.objects.get(id=bbb_id)
        except Exception as e:
            return Response({'errors': True, 'message': 'Meeting xonasi topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'errors': True, 'massegs': "O'qituvchi ID raqami yuborilmadi"},
                            status=status.HTTP_404_NOT_FOUND)

        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            with transaction.atomic():
                try:
                    bbb.add_restart_field(bbb.name, bbb.maxParticipants)
                    bbb.save()
                except Exception as e:
                    transaction.set_rollback(True)
                    return Response({"success": False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                # print(my_model.id)
                try:
                    base_url = BigbluebuttonMain.objects.last()
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "
                except:
                    transaction.set_rollback(True)
                    data = {'success': False, 'message': 'Meeting url malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    send_url = Bigbluebutton_sub.objects.get(uniq_id=1)
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "
                except:
                    transaction.set_rollback(True)
                    data = {'success': False,
                            'message': 'Meeting url metod malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    if not bbb.status:
                        fields_and_values = bbb.__dict__
                        query = ""
                        for index, (field_name, field_value) in enumerate(sorted(fields_and_values.items())):
                            if field_name not in ['id', 'created_at', 'updated_at', 'status_action', '_state', 'status',
                                                  'team_id']:
                                if field_value:
                                    if index == len(fields_and_values) - 1:
                                        if field_name in ['name']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        elif field_name in ['attendeePW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        elif field_name in ['moderatorPW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        elif field_name in ['welcome']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8"))
                                        else:
                                            if type(field_value) == bool:
                                                query += field_name + '=' + str(field_value).lower()
                                            else:
                                                query += field_name + '=' + str(field_value)
                                    else:
                                        if field_name in ['name']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        elif field_name in ['attendeePW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        elif field_name in ['moderatorPW']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        elif field_name in ['welcome']:
                                            query += field_name + '=' + urllib.parse.quote(
                                                str(field_value).encode("utf-8")) + '&'
                                        else:
                                            if type(field_value) == bool:
                                                query += field_name + '=' + str(field_value).lower() + '&'
                                            else:
                                                query += field_name + '=' + str(field_value) + '&'
                        xquery = send_url.url_method + query
                        checksum = checksum_genration(xquery, base_url.sicret_key)
                        url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
                        response = requests.get(url)
                        if response.status_code == 200:
                            parsed_dict = xmltodict.parse(response.text)
                            if parsed_dict['response']['returncode'] == 'SUCCESS':
                                bbb.status = True
                                bbb.redirect = True
                                bbb.save()
                            else:
                                bbb.status = False
                                bbb.redirect = True
                                bbb.save()
                            return Response({'success': True, 'results': parsed_dict['response']},
                                            status=status.HTTP_200_OK)
                        else:
                            transaction.set_rollback(True)
                            return Response({'success': False, 'message': "Meeting serverida muammo mavjud. Adminga murojaat qiling."},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        transaction.set_rollback(True)
                        return Response({'success': False, 'message': 'Meeting serverida muammo mavjud. Adminga murojaat qiling.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    transaction.set_rollback(True)
                    return Response({'succes': False, 'message': str(e)},
                                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class TaskViewTeacher(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(
        query_serializer=TaskallsxemSerializer
    )
    def get(self, request, *args, **kwargs):
        #teacher_id = self.request.query_params.get('teacher_id', None)
        topic_id = self.request.query_params.get('topic_id', None)
        user=request.user
        teacher_id = user.employee.employee_id_number
        if teacher_id is None:
            return Response({'error': True, 'message': 'O`qituvchi idisi kirtish majburiy '},
                            status=status.HTTP_404_NOT_FOUND)
        if topic_id is None:
            return Response({'error': True, 'message': 'Mavzular idisi kirtish majburiy '},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                tasks = Task.objects.filter(topic_id_task_id=topic_id)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            serialzer = TaskviewSerializer(tasks, many=True)
            return Response({'error': False, 'results': serialzer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class TaskdetailTeacher(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def get(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(id=pk)
            serialzer = TaskviewSerializer(task, many=False)
            return Response({'error': False, 'results': serialzer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)


class TaskcreateTeacher(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(request_body=TaskcreatesxemSerializer)
    def post(self, request, *args, **kwargs):
        teacher = Check_teacher(request.data['teacher_id'])
        if teacher['check']:
            request.data['teacher_id'] = teacher['teacher'].id
            serailizer = TaskcreateSerializer(data=request.data)
            if serailizer.is_valid():
                serailizer.save()
                return Response(
                    {
                        'error': False,
                        'results': serailizer.data
                    }, status=status.HTTP_201_CREATED
                )
            return Response({'error': True, 'message': serailizer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class TaskupdateTeacher(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(request_body=TaskcreatesxemSerializer)
    def patch(self, request, *args, **kwargs):
        teacher = Check_teacher(request.data['teacher_id'])
        if teacher['check']:
            try:
                obj = Task.objects.get(id=request.data['id'])
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            task = TaskFUpdateSerializer(obj, data=request.data)
            if task.is_valid():
                task.save()
                return Response(
                    {
                        'error': False,
                        'results': task.data
                    }, status=status.HTTP_200_OK
                )
            return Response({'error': True, 'message': task.errors['message']}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Taskfileadd(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(request_body=Task_file_add_sxemSerializer)
    def post(self, request, task_id, *args, **kwargs):
        if not request.FILES:
            return Response({'error': True, 'message': 'Fayilar topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(request.data['teacher_id'])
        if teacher['check']:
            try:
                task = Task.objects.get(id=task_id)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            with transaction.atomic():
                try:
                    files = request.FILES.getlist('task_files')
                    for file in files:
                        task_file = Task_file()
                        task_file.task_file = file
                        task_file.task = task
                        task_file.save()
                except Exception as ex:
                    transaction.set_rollback(True)
                    return Response(
                        {'error': True, 'message': 'Fayil birktrishda muamo bor!',
                         'er_message': str(ex)},
                        status=status.HTTP_400_BAD_REQUEST)
            try:
                task_fiels = Task_file.objects.filter(task=task)
                if task_fiels.count() > 0:
                    task.file_status = True
                    task.save()
                serializer = Task_fileSerializer(task_fiels, many=True)
                return Response(
                    {'error': False, 'message': 'Topshiriqga birktrilgan fayilar qo`shildi!',
                     'results': serializer.data},
                    status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response(
                    {'error': True, 'message': 'Topshirqga biriktrildi fayilar lekin malumot serializerlanmadi!',
                     'er_message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Taskfiledelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def delete(self, request, task_id, teacher_id, pk, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            teacher = Check_teacher(teacher_id)
        except Exception as ex:
            return Response({'error': True, 'message': 'O`qtuvchisini idisi kirtilmagan!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if teacher['check']:
            try:
                task_file = Task_file.objects.get(id=pk)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            try:
                if task == task_file.task:
                    task_file.delete()
                    task_fiels = Task_file.objects.filter(task=task)
                    if task_fiels.count() == 0:
                        task.file_status = False
                        task.save()
                    return Response({'error': False, 'message': 'Birktrilgan fayil o`chirildi!'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'error': True, 'message': 'Belgilangan Fayilar shu topshiriq ichda joylashmagan!'},
                                    status=status.HTTP_404_NOT_FOUND)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Taskgroupview(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(query_serializer=TaskgroupsxemSerializer)
    def get(self, request, *args, **kwargs):
        teacher_id = self.request.query_params.get('teacher_id', None)
        task_id = self.request.query_params.get('task_id', None)
        if teacher_id is None:
            return Response({'error': True, 'message': 'O`qituvchi idisi kirtish majburiy '},
                            status=status.HTTP_404_NOT_FOUND)
        if task_id is None:
            return Response({'error': True, 'message': 'Topshirq idisi kirtish majburiy '},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                task = Task.objects.get(id=task_id)
            except Exception as ex:
                return Response(
                    {'error': True, 'message': 'Topshiriq topilmadi!'}, status=status.HTTP_400_BAD_REQUEST
                )
            try:
                group = task.topic_id_task.content_id_topic.group.all()
                serializer = Task_groupSerializer(group, many=True)
                return Response({'error': False, 'message': 'Natija bor', 'results': serializer.data},
                                status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Taskstudentview(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(query_serializer=TaskstudentsxemSerializer)
    def get(self, request, *args, **kwargs):
        teacher_id = self.request.query_params.get('teacher_id', None)
        group_id = self.request.query_params.get('group_id', None)
        if teacher_id is None:
            return Response({'error': True, 'message': 'O`qituvchi idisi kirtish majburiy '},
                            status=status.HTTP_404_NOT_FOUND)
        if group_id is None:
            return Response({'error': True, 'message': 'Gurux idisi kirtish majburiy '},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                group = Group.objects.get(id=group_id)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
            try:
                students = Student.objects.filter(group=group)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
            try:
                serializer = TaskStudentSerializer(students, many=True)
                return Response({'error': False, 'message': 'Natija bor', 'results': serializer.data},
                                status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Taskgoupadd(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(request_body=TaskGorupAddSerializer)
    def post(self, request, task_id, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskGorupAddSerializer(data=request.data)
        if serializer.is_valid():
            teacher_id = serializer.validated_data.get('teacher_id', None)
            groups = serializer.validated_data.get('groups', None)
            teacher = Check_teacher(teacher_id)
            if teacher['check']:
                with transaction.atomic():
                    for group in groups:
                        try:
                            one_group = Group.objects.get(id=group)
                        except Exception as ex:
                            transaction.set_rollback(True)
                            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
                        try:
                            # Task.objects.filter()
                            # print(count)
                            students = Student.objects.filter(group=one_group)
                            for student in students:
                                tasks = Task.objects.filter(topic_id_task=task.topic_id_task)
                                count = 0
                                chcek = False
                                for item in tasks:
                                    try:
                                        tac = Task_students.objects.get(tasks_id__id=item.id,
                                                                        task_student_id__id=student.id,
                                                                        task_group_id__id=student.group.id)
                                        count = count + 1
                                        chcek = True
                                    except Task_students.DoesNotExist:
                                        pass
                                obj = Task_students()
                                obj.task_group_id = one_group
                                obj.task_student_id = student
                                obj.status_control = True
                                obj.tasks_id = task
                                obj.teacher_id = teacher['teacher']
                                obj.task_check = False
                                if chcek:
                                    obj.number = count + 1
                                else:
                                    if task.topic_id_task.number == 1:
                                        obj.is_status = True
                                    obj.number = count + 1
                                obj.save()
                            task_studnet = Task_students.objects.filter(tasks_id=task).count()
                            if task_studnet > 0:
                                task.group_status = True
                                task.save()
                        except Exception as ex:
                            transaction.set_rollback(True)
                            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
                    return Response(
                        {'error': False, 'message': 'Muamo mavjud emas! Topshirqga qo`shildi guruhlar ...'},
                        status=status.HTTP_200_OK)
            else:
                return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': True, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# bugun qilish kere!
class Taskgoupdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def delete(self, request, task_id, teacher_id, pk, *args, **kwargs):
        try:
            teacher = Check_teacher(teacher_id)
        except Exception as ex:
            return Response({'error': True, 'message': 'O`qtuvchi toplmadi'}, status=status.HTTP_400_BAD_REQUEST)

        if teacher['check']:
            try:
                task = Task.objects.get(id=task_id)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            try:
                group = Group.objects.get(id=pk)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            try:
                with transaction.atomic():
                    students = Task_students.objects.filter(tasks_id=task, task_group_id=group)
                    for item in students:
                        if item.uploading_file_status:
                            transaction.set_rollback(True)
                            return Response(
                                {'error': True, 'message': 'O`avuchi yuklagan uji Gurxni ajartib bo`lmidi!'},
                                status=status.HTTP_404_NOT_FOUND)
                        item.delete()
                    task_studnet = Task_students.objects.filter(tasks_id=task).count()
                    if task_studnet == 0:
                        task.group_status = False
                        task.save()
                return Response({'error': False, 'message': 'Guruh o`chirildi!'}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class TaskCreatewithfile(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(request_body=TaskFilescreateschemaSerializer)
    def post(self, request, *args, **kwargs):
        if not request.FILES:
            return Response({'error': True, 'message': 'Fayilar topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            teacher = Check_teacher(request.data['teacher_id'])
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        if teacher['check']:
            request.data.update({'teacher_id': teacher['teacher'].id})
            task = Taskcreatewithfile(data=request.data)
            if task.is_valid():
                with transaction.atomic():
                    try:
                        task.save()
                    except ValidationError as ex:
                        transaction.set_rollback(True)
                        return Response({'error': True, 'message': ex.detail},
                                        status=status.HTTP_400_BAD_REQUEST)

                    try:
                        obj_task = Task.objects.get(id=task.data['id'])
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

                    task_files_data = {'task_files': request.FILES.getlist('task_files'), 'task_id': task.data['id']}

                    task_files = TaskFilecreateSerializer(data=task_files_data)
                    if task_files.is_valid():
                        try:
                            task_files.save()
                        except ValidationError as ex:
                            transaction.set_rollback(True)
                            return Response({'error': True, 'message': ex.detail},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        transaction.set_rollback(True)
                        return Response({'error': True, 'message': task_files.errors},
                                        status=status.HTTP_400_BAD_REQUEST)

                    try:
                        serialzer = TaskviewSerializer(obj_task, many=False)
                        return Response({'error': False, 'results': serialzer.data},
                                        status=status.HTTP_201_CREATED)
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': True, 'message': task.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Taskactionstudentview(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def get(self, request, task_id, group_id, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            studnets = Task_students.objects.filter(tasks_id=task, task_group_id=group)
            serializer = TaskactionSerializer(studnets, many=True)
            return Response({'error': False, 'results': serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class Task_student_actions_change(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def post(self, request, task_id, group_id, pk, *args, **kwargs):
        teacher_id = request.data.get('teacher_id', None)
        status_control = request.data.get('status', None)
        if teacher_id is None:
            return Response({'error': True, 'message': 'teacher_id yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_400_BAD_REQUEST)
        if status_control is None:
            return Response({'error': True, 'message': 'status_control yuborilgan jsonda  mavjud emas'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            task = Task.objects.get(id=task_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            student = Student.objects.get(id=pk)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        try:
            teacher = Check_teacher(request.data['teacher_id'])
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        if teacher['check']:
            try:
                task_studnet = Task_students.objects.get(task_group_id=group, task_student_id=student, tasks_id=task)
                task_studnet.status_control = status_control
                task_studnet.save()
                return Response({'error': False, 'message': 'Status o`zgardi!'}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Taskfupdateview(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def patch(self, request, pk, *args, **kwargs):
        teacher_id = request.data.get('teacher_id')
        if teacher_id is None:
            return Response({'error': True, 'message': 'teacher_id yuborilgan jsonda mavjud emas'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher = Check_teacher(teacher_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

        mutable_data = request.data.copy()  # Make a mutable copy of the QueryDict
        mutable_data.update({'teacher_id': teacher['teacher'].id})

        try:
            instance = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"error": True, 'message': 'Topshiriq topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if teacher['check']:
            with transaction.atomic():
                serializer = TaskFUpdateSerializer(instance, data=mutable_data, partial=True)  # Partial update
                if serializer.is_valid(raise_exception=True):
                    try:
                        serializer.save()
                    except ValidationError as ex:
                        transaction.set_rollback(True)
                        return Response({'error': True, 'message': ex.detail},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    transaction.set_rollback(True)
                    # return Response({'error': True, 'message': "salom"}, status=status.HTTP_400_BAD_REQUEST)
                # else:
                #     message = serializer.errors
                #     transaction.set_rollback(True)
                #     return Response({'error': True, 'message':message},
                #                     status=status.HTTP_400_BAD_REQUEST)

                # Handling task files update
                try:
                    task_files = TaskFileupdateSerializer(data=mutable_data)
                    if task_files.is_valid():
                        for file in task_files.validated_data.get('task_files', []):
                            try:
                                obj_task_file = Task_file()
                                obj_task_file.task_file = file
                                obj_task_file.task = instance
                                obj_task_file.save()
                            except Exception as ex:
                                transaction.set_rollback(True)
                                return Response({'error': True, 'message': str(ex)},
                                                status=status.HTTP_400_BAD_REQUEST)
                    else:
                        transaction.set_rollback(True)
                        return Response({'error': True, 'message': serializer.errors},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Exception as ex:
                    return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

                serialzer = TaskviewSerializer(instance, many=False)
                return Response({'error': False, 'results': serialzer.data},
                                status=status.HTTP_200_OK)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class GetScorelimit(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(query_serializer=GetScorelimitSerailizer)
    def get(self, request, *args, **kwargs):
        teacher_id = self.request.query_params.get('teacher_id', None)
        task_id = self.request.query_params.get('task_id', None)
        try:
            teacher = Check_teacher(teacher_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        if teacher['check']:
            try:
                task = Task.objects.get(id=task_id)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            try:
                answare = countremain(task)
                if answare['error']:
                    return Response({'error': False, 'results': answare['results']}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': True, 'results': answare['message']}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class GetScoreTopiclimit(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    @swagger_auto_schema(query_serializer=GetScoreTopiclimitSerailizer)
    def get(self, request, *args, **kwargs):
        #teacher_id = self.request.query_params.get('teacher_id', None)
        user=request.user
        teacher_id = user.employee.employee_id_number
        topic_id = self.request.query_params.get('topic_id', None)
        try:
            teacher = Check_teacher(teacher_id)
        except Exception as ex:
            return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        if teacher['check']:
            try:
                topic = Topic.objects.get(id=topic_id)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
            try:
                answare = countremaintopic(topic)
                if answare['error']:
                    return Response({'error': False, 'results': answare['results']}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': True, 'results': answare['message']}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({'error': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': teacher['message']}, status=status.HTTP_404_NOT_FOUND)


class Content_teacher_list_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request):
        try:
            content_teacher = Content_teacher.objects.filter(
                teacher_id=request.user.employee,
                content_id__semestr_action=True
            )
            serializer = Content_teacherList_Serializer(content_teacher, many=True)
            data = serializer.data

            # Har bir obyektga total_count_students qo'shish
            for content in data:
                content['total_count_students'] = sum(
                    group['student_count'] for group in content['group_by']
                )

            return Response({"success": True, 'results': data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(
                {"error": True, 'message': str(ex)},
                status=status.HTTP_400_BAD_REQUEST
            )


class Room_list_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request):
        try:
            lesson_rooms = LessonRoom.objects.filter(teacher_id=request.user.employee)
            seralizer = LessonRoomListSerialzier(lesson_rooms, many=True)
            return Response({"success": True, 'results': seralizer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(
                {"error": True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST
            )


class Room_Lesson_Create_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def post(self, request, format=None):
        # print(f'{request.data=}')
        try:

            custom_data = request.data.copy()

            custom_data['teacher_id'] = request.user.employee.id
            data = LessonRoomCreateSerialzer(data=custom_data)

            # print(f'{data=}')
            if data.is_valid():
                try:
                    conntects = data.validated_data['connect']
                    patoc_students = 0
                    for conntect in conntects:
                        connect_teacher = Content_teacher.objects.get(
                            id=conntect)
                        groups = connect_teacher.group_by.all()
                        total_students = 0
                        for group in groups:
                            student_counts = group.student_group.all().count()
                            total_students = total_students + student_counts
                        patoc_students = patoc_students + total_students

                except Exception as ex:
                    return Response({"success": False, 'message': 'O`quvsichlar soni olishda hatolik bor!'},
                                    status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():
                    lesson_room_instance = data.save()
                    if patoc_students > 230:
                        transaction.set_rollback(True)
                        return Response({'message': 'Talabalar soni chegaradan oshib ketdi (max=230)'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    try:
                        my_model = Bigbluebutton_Model()
                        my_model.add_random_field(data.data.get('name'), patoc_students)
                        my_model.team_id = lesson_room_instance
                        my_model.save()
                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response({"success": False, 'message': e}, status=status.HTTP_400_BAD_REQUEST)
                    # print(my_model.id)
                    try:
                        base_url = BigbluebuttonMain.objects.last()
                        "URl qaytarish qo`shiladigan hona uchun mentor uchun "
                    except:
                        transaction.set_rollback(True)
                        data = {'success': False, 'message': 'Bigbluebutton base_url malumotlar omboridan topilmadi'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    try:
                        send_url = Bigbluebutton_sub.objects.get(uniq_id=1)
                        "URl qaytarish qo`shiladigan hona uchun mentor uchun "

                    except:

                        transaction.set_rollback(True)
                        data = {'success': False,
                                'message': 'Bigbluebutton send_url metod malumotlar omboridan topilmadi'}
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    try:
                        if not my_model.status:
                            fields_and_values = my_model.__dict__
                            query = ""
                            for index, (field_name, field_value) in enumerate(sorted(fields_and_values.items())):
                                if field_name not in ['id', 'created_at', 'updated_at', 'status_action', '_state',
                                                      'team_id', 'status']:
                                    if field_value:
                                        if index == len(fields_and_values) - 1:
                                            if field_name in ['name']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            elif field_name in ['attendeePW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            elif field_name in ['moderatorPW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            elif field_name in ['welcome']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8"))
                                            else:
                                                if type(field_value) == bool:
                                                    query += field_name + '=' + str(field_value).lower()
                                                else:
                                                    query += field_name + '=' + str(field_value)
                                        else:
                                            if field_name in ['name']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            elif field_name in ['attendeePW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            elif field_name in ['moderatorPW']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            elif field_name in ['welcome']:
                                                query += field_name + '=' + urllib.parse.quote(
                                                    str(field_value).encode("utf-8")) + '&'
                                            else:
                                                if type(field_value) == bool:
                                                    query += field_name + '=' + str(field_value).lower() + '&'
                                                else:
                                                    query += field_name + '=' + str(field_value) + '&'
                            xquery = send_url.url_method + query
                            checksum = checksum_genration(xquery, base_url.sicret_key)
                            url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
                            response = requests.get(url)
                            if response.status_code == 200:
                                parsed_dict = xmltodict.parse(response.text)
                                if parsed_dict['response']['returncode'] == 'SUCCESS':
                                    my_model.status = True
                                    my_model.redirect = True
                                    my_model.save()
                                else:
                                    my_model.status = False
                                    my_model.redirect = True
                                    my_model.save()
                                return Response({'success': True, 'results': parsed_dict['response']},
                                                status=status.HTTP_201_CREATED)
                            else:

                                transaction.set_rollback(True)
                                return Response({'success': False, 'message': 'bigbluebutton javob notogri'},
                                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            transaction.set_rollback(True)
                            return Response({'success': False, 'message': 'bigbluebutton xona ochilgan'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:

                        transaction.set_rollback(True)
                        return Response({'succes': False, 'message': str(e)},
                                        status=status.HTTP_404_NOT_FOUND)

                return Response(data.data, status=status.HTTP_201_CREATED)
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response(
                {"error": True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST
            )


class Room_Lesson_Update_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request, pk, format=None):
        try:
            # Fetch the LessonRoom object by its primary key (pk)
            lesson_room = LessonRoom.objects.get(pk=pk)

            # Serialize the object
            serializer = LessonRoomListSerialzier(lesson_room)

            # Return the serialized data as a response
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LessonRoom.DoesNotExist:
            # Return an error if the object is not found
            return Response(
                {"error": True, "message": "Lesson room not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            # Handle any other exceptions
            return Response(
                {"error": True, "message": str(ex)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, pk, format=None):
        try:
            lesson_room = LessonRoom.objects.get(pk=pk)
            custom_data = request.data.copy()
            serializer = RoomLessonUpdateSerializer(lesson_room, data=custom_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except LessonRoom.DoesNotExist:
            return Response(
                {"error": True, 'message': "Lesson room not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"error": True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, pk, format=None):
        try:
            lesson_room = LessonRoom.objects.get(pk=pk)
            custom_data = request.data.copy()
            serializer = RoomLessonUpdateSerializer(lesson_room, data=custom_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except LessonRoom.DoesNotExist:
            return Response(
                {"error": True, 'message': "Lesson room not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"error": True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk, format=None):
        try:
            # Fetch the LessonRoom object by its primary key
            lesson_room = LessonRoom.objects.get(pk=pk)
            lesson_room.team_bigbluebutton.delete()
            # Delete the object
            lesson_room.delete()

            # Return a success response
            return Response(
                {"message": "Lesson room successfully deleted."},
                status=status.HTTP_204_NO_CONTENT
            )
        except LessonRoom.DoesNotExist:
            # Return an error if the object is not found
            return Response(
                {"error": True, "message": "Lesson room not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            # Handle any other exceptions
            return Response(
                {"error": True, "message": str(ex)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LessonRoom_bbb_create(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def post(self, request):
        custom_data = request.data.copy()
        custom_data['teacher_id'] = request.user.employee.employee_id_number
        serializer = 'asd'  # BigbluebuttonCreateLessonRoomSerial(data=custom_data)
        if serializer.is_valid():
            try:
                item = LessonRoom.objects.get(id=serializer.data['lesson_room'])
            except LessonRoom.DoesNotExist:
                return Response({'errors': True, 'massegs': 'Topic topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
            teacher = Check_teacher(serializer.data['teacher_id'])
            if teacher['check']:
                return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
