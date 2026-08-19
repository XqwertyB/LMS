from wsgiref.util import FileWrapper

from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from config.permissions import AllowOnlyTrustedOrigins
from learning_process.models import Curriculum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
import datetime
from employee.models import Employee
from content.models import Content, Content_teacher, Topic, Task, Task_students, Student_file
from group.models import Group
from content.serializers import ContentViewSerializer
from teacher.serializers import Teacher_TopicSerializers, Teacher_VideoSerializers
import datetime
from students.models import Student
from .serializers import TaskSerializers, Task_studentsSerializers, TasktakeSerializers, TopicSerializers, \
    LessonRoom_list_Serializer
from django.db import transaction
from django.utils import timezone
from bigbluebutton.models import Bigbluebutton_Model, BigbluebuttonMain, Bigbluebutton_sub
import xmltodict
import urllib.parse
import requests
from bigbluebutton.checksum_genrate import checksum_genration
from user.permission import (
    IsAdmin,
    IsStudent
)
from rest_framework.permissions import IsAuthenticated
from content.models import LessonRoom


class ViewStudentSubjects_active(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent,]
    def get(self, request, *args, **kwargs):
        # student_id_number = self.request.query_params.get('student_id_number')
        group_id = self.request.query_params.get('group_id')
        if group_id is None:
            return Response({'errors': True, 'message': 'Guruh id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            contents = Content.objects.filter(group=group, semestr_action=True)
            serdata = ContentViewSerializer(contents, many=True)
            return Response({'succes': 'True', 'results': serdata.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewStudentSubjects_inactive(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        # student_id_number = self.request.query_params.get('student_id_number')
        group_id = self.request.query_params.get('group_id')
        if group_id is None:
            return Response({'errors': True, 'message': 'Guruh id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            contents = Content.objects.filter(group=group, semestr_action=False)
            serdata = ContentViewSerializer(contents, many=True)
            return Response({'succes': 'True', 'results': serdata.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewSutudentSubject_topic(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        content_id = self.request.query_params.get('content_id')
        group_id = self.request.query_params.get('group_id')
        if group_id is None:
            return Response({'errors': True, 'message': 'Guruh id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if content_id is None:
            return Response({'errors': True, 'message': 'content id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            content = Content.objects.get(id=content_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            content_teacher = Content_teacher.objects.filter(group_by=group, content_id=content)
            ### Jabbor aka vaqt intervali gaplashiladi
            connect = content_teacher[0]
            topics = Topic.objects.filter(content_id_topic=content, content_teacher_connect=connect)
            serilazer = TopicSerializers(topics, many=True)
            return Response({'succes': 'True', 'results': serilazer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewSutudenttopic_one(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('topic_id')
        if topic_id is None:
            return Response({'errors': True, 'message': 'topic_id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serilazer = Teacher_TopicSerializers(topic, many=False)
            return Response({'succes': 'True', 'results': serilazer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewTaskStudents(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('topic_id')
        student_id = self.request.query_params.get('student_id')
        if topic_id is None:
            return Response({'errors': True, 'message': 'topic_id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if student_id is None:
            return Response({'errors': True, 'message': 'student_id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(id=student_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            connect_tasks = Task_students.objects.filter(task_student_id=student,
                                                         tasks_id__topic_id_task=topic)
            serializers = Task_studentsSerializers(connect_tasks, many=True)
            return Response({'success': True, 'results': serializers.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewTasktake(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def post(self, request, *args, **kwargs):
        if not request.FILES:
            return Response({'succes': False, 'message': 'Fayilar topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        answare = TasktakeSerializers(data=request.data)
        if answare.is_valid():
            try:
                student = Student.objects.get(id=answare.validated_data['student_id'])
            except Exception as e:
                return Response({'succes': False, 'massage': str(e)}, status=status.HTTP_404_NOT_FOUND)
            try:
                task = Task.objects.get(id=answare.validated_data['tasks_id'])
            except Exception as e:
                return Response({'succes': False, 'massage': str(e)}, status=status.HTTP_404_NOT_FOUND)
            try:
                task_student = Task_students.objects.get(id=answare.validated_data['student_connect_task_id'])
            except Exception as e:
                return Response({'succes': False, 'massage': str(e)}, status=status.HTTP_404_NOT_FOUND)
            if task_student.task_student_id != student:
                return Response({'succes': False, 'massage': 'topshirq va student boglanish xato!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if task_student.tasks_id != task:
                return Response({'succes': False, 'massage': 'topshirq va topshirq boglanish xato!'},
                                status=status.HTTP_400_BAD_REQUEST)
            take_task = Student_file.objects.filter(student_task_id=student, take_task=task)
            current_datetime = timezone.now()
            if task.start_date > current_datetime:
                return Response({'errors': True, 'message': 'Topshiriq muddati hali boshlanmagan'},
                                status=status.HTTP_400_BAD_REQUEST)
            if task.end_date < current_datetime:
                return Response({'errors': True, 'message': 'Topshiriq muddati o`tib ketgan'},
                                status=status.HTTP_400_BAD_REQUEST)
            with transaction.atomic():
                if take_task.count() < task.attempts:
                    try:
                        as_take_task = Student_file()
                        as_take_task.student_file = answare.validated_data['student_file']
                        as_take_task.file_date_sending = current_datetime
                        as_take_task.take_task = task
                        as_take_task.comment = answare.validated_data['comment']
                        as_take_task.student_task_id = student
                        as_take_task.task_connect = task_student
                        as_take_task.number = (task.attempts + take_task.count()) % task.attempts + 1
                        as_take_task.save()
                        task_student.uploading_file_status = True
                        task_student.save()
                        return Response({'success': True, 'message': 'Topshiriq fayil yuklandi!'},
                                        status=status.HTTP_201_CREATED)
                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    task_student.number_status = True
                    task_student.save()
                    return Response({'errors': True, 'message': 'Urunishlar soni tugadi.'},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': True, 'message': answare.errors}, status=status.HTTP_400_BAD_REQUEST)


class ViewSutudentSubject_topic_task(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        content_id = self.request.query_params.get('content_id')
        group_id = self.request.query_params.get('group_id')
        if group_id is None:
            return Response({'errors': True, 'message': 'Guruh id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if content_id is None:
            return Response({'errors': True, 'message': 'content id mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            content = Content.objects.get(id=content_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            content_teacher = Content_teacher.objects.filter(group_by=group, content_id=content)
            connect = content_teacher[0]
            topics = Topic.objects.filter(content_id_topic=content, content_teacher_connect=connect).order_by(
                '-created_at')
            serializer = Teacher_TopicSerializers(topics, many=True)

            video_files = {}
            for topic in topics:
                videos = Teacher_VideoSerializers(topic.topic_videos, many=True).data
                for video in videos:
                    video_files[video['id']] = video['vide_file']

            response = StreamingHttpResponse(self.stream_video(video_files), content_type='video/mp4')
            return response
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def stream_video(self, video_files):
        for video_id, video_file in video_files.items():
            video_path = video_file.path
            with open(video_path, 'rb') as file:
                wrapper = FileWrapper(file)
                for chunk in wrapper:
                    yield chunk


class Takebigbluebutton(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('topic_id')
        group_id = self.request.query_params.get('group_id')
        bbb_id = self.request.query_params.get('bbb_id')
        if group_id is None:
            return Response({'errors': True, 'message': 'Guruh idsi mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if topic_id is None:
            return Response({'errors': True, 'message': 'Mavzular idsi mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if bbb_id is None:
            return Response({'success': False, 'message': 'bbb_id mavjud emas.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            base_url = BigbluebuttonMain.objects.last()
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "
        except:
            data = {'success': False, 'message': 'base_url malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            send_url = Bigbluebutton_sub.objects.get(uniq_id=5)
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "

        except:
            data = {'success': False, 'message': 'send_url metod malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            obj = Bigbluebutton_Model.objects.get(pk=bbb_id)
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "
        except:
            data = {'success': False, 'message': 'id malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            query = ""
            # Print field names and their values
            meetingID = str(obj.meetingID)
            query += 'meetingID=' + meetingID
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
                        {'success': False, 'message': parsed_dict['response']['message']},
                        status=status.HTTP_404_NOT_FOUND)
                return Response({'success': True, 'results': parsed_dict}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'bigbluebutton javob notogri'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': 'bigbluebutton javob notogri'},
                            status=status.HTTP_400_BAD_REQUEST)


class TaskcheckView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        student_id = self.request.query_params.get('student_id')
        topic_id = self.request.query_params.get('topic_id')
        if student_id is None:
            return Response({'errors': True, 'message': 'Student idsi mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if topic_id is None:
            return Response({'errors': True, 'message': 'Topic idsi mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            student = Student.objects.get(id=student_id)
        except Exception as e:
            return Response({'succes': False, 'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            return Response({'succes': False, 'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
        try:
            check = False
            tasks = Task_students.objects.filter(task_student_id=student, tasks_id__topic_id_task=topic,
                                                 mark_status=True).order_by('-created_at')
            for task in tasks:
                if task.mark < task.tasks_id.score * 0.6:
                    check = True
                    break
            tasks = Task_students.objects.filter(task_student_id=student, tasks_id__topic_id_task=topic,
                                                 mark_status=False).order_by('-created_at')

            for task in tasks:
                if check:
                    task.is_status = False
                    task.save()
                else:
                    task.is_status = True
                    task.save()
        except Exception as e:
            return Response({'succes': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'succes': True}, status=status.HTTP_200_OK)


class TasktimecheckView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        student_id = self.request.query_params.get('student_id')
        if student_id is None:
            return Response({'errors': True, 'message': 'Student idsi mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            student = Student.objects.get(id=student_id)
        except Exception as e:
            return Response({'succes': False, 'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
        try:
            current_datetime = timezone.now()
            tasks = Task_students.objects.filter(task_student_id=student)
            for task in tasks:
                if task.tasks_id.end_date < current_datetime:
                    task.time_status = False
                    task.save()
                elif task.tasks_id.start_date > current_datetime:
                    task.time_status = False
                    task.save()
                else:
                    task.time_status = True
                    task.save()
        except Exception as e:
            return Response({'succes': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'succes': True}, status=status.HTTP_200_OK)


class ResultsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent,]

    def get(self, request, *args, **kwargs):
        print(request.user.student)
        tasks_mark = Task_students.objects.filter(task_student_id=request.user.student)

        print(tasks_mark)
        return Response({
            'success': True
        }, status=status.HTTP_200_OK)


class Lesson_Room_list_View(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent,]

    def get(self, request, *args, **kwargs):
        try:
            student_group = request.user.student.group
            lesson_room = LessonRoom.objects.filter(connect__group_by=student_group)
            serializer = LessonRoom_list_Serializer(lesson_room, many=True)
            return Response(
                {
                    'success': True,
                    'results': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as ex:
            return Response(
                {'success': True, 'message': str(ex)}, status=status.HTTP_400_BAD_REQUEST
            )


class TakebigbluebuttonLesson(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent, ]
    def get(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('lesson_room')
        group_id = self.request.query_params.get('group_id')
        bbb_id = self.request.query_params.get('bbb_id')
        if group_id is None:
            return Response({'errors': True, 'message': 'Guruh idsi mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if topic_id is None:
            return Response({'errors': True, 'message': 'Mavzular idsi mavjud emas!'}, status=status.HTTP_404_NOT_FOUND)
        if bbb_id is None:
            return Response({'success': False, 'message': 'bbb_id mavjud emas.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            topic = LessonRoom.objects.get(id=topic_id)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            base_url = BigbluebuttonMain.objects.last()
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "
        except:
            data = {'success': False, 'message': 'base_url malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            send_url = Bigbluebutton_sub.objects.get(uniq_id=5)
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "

        except:
            data = {'success': False, 'message': 'send_url metod malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            obj = Bigbluebutton_Model.objects.get(pk=bbb_id)
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "
        except:
            data = {'success': False, 'message': 'id malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        try:
            query = ""
            # Print field names and their values
            meetingID = str(obj.meetingID)
            query += 'meetingID=' + meetingID
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
                        {'success': False, 'message': parsed_dict['response']['message']},
                        status=status.HTTP_404_NOT_FOUND)
                return Response({'success': True, 'results': parsed_dict}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'bigbluebutton javob notogri'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': 'bigbluebutton javob notogri'},
                            status=status.HTTP_400_BAD_REQUEST)


class Checkin_Join(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (AllowOnlyTrustedOrigins,IsStudent,)

    def bbb_baseurl(self):
        base_url = BigbluebuttonMain.objects.last()
        if not base_url:
            raise ValueError("Asosiy manzil malumotlar omboridan topilmadi, Adminga murojaat qiling!")
        return base_url

    def bbb_sendingurl(self, number):
        try:
            return Bigbluebutton_sub.objects.get(uniq_id=number)
        except Bigbluebutton_sub.DoesNotExist:
            raise ValueError("send_url metod malumotlar omboridan topilmadi")

    def find_room(self, bbb_id):
        try:
            return Bigbluebutton_Model.objects.get(pk=bbb_id)
        except Bigbluebutton_Model.DoesNotExist:
            raise ValueError("Video konferensiya IDsi malumotlar omboridan topilmadi, Adminga murojaat qiling!")

    def room_status(self, base_url, room):
        send_url = self.bbb_sendingurl(5)
        try:
            meetingID = str(room.meetingID)
            query = f'meetingID={meetingID}'
            xquery = send_url.url_method + query
            checksum = checksum_genration(xquery, base_url.sicret_key)

            url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
            response = requests.get(url)

            if response.status_code == 200:
                parsed_dict = xmltodict.parse(response.text)
                check_failed = parsed_dict['response']['returncode']

                if check_failed == 'FAILED':
                    if 'messageKey' in parsed_dict['response'] and parsed_dict['response']['messageKey'] == 'some_key':
                        raise ValueError('Video dars hali boshlanmagan!, O`qituvchiga murojaat qiling!')
                    room.status = False
                    room.save()
                    return False  # Room not active
                return True  # Room is active
            else:
                raise ValueError('Video dars tizimga murojaat javobi noto‘g‘ri. Adminga murojaat qiling!')

        except Exception as e:
            raise ValueError(f"BigBlueButton javobi noto'g'ri: {str(e)}")

    def join_room(self, base_url, room, user):
        send_url = self.bbb_sendingurl(2)
        try:
            if not room.status:
                return Response({'error': 'Video dars hali boshlanmagan!'}, status=status.HTTP_400_BAD_REQUEST)
            meetingID = urllib.parse.quote(str(room.meetingID).encode("utf-8"))
            fullName = urllib.parse.quote(str(user.full_name).encode("utf-8"))
            attendeePW = urllib.parse.quote(str(room.attendeePW).encode("utf-8"))
            redirect = str(room.redirect).lower()
            userID = urllib.parse.quote(str(user.id).encode("utf-8"))
            query = f'fullName={fullName}&meetingID={meetingID}&password={attendeePW}&redirect={redirect}&userID={userID}'

            # Generate checksum
            checksum = checksum_genration(f'{send_url.url_method}{query}', base_url.sicret_key)

            # Construct the final URL
            url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
            return url
        except Exception as ex:
            return Response({'error': 'Video dars xona kirish manzil berishda xatolik bor,Adminga murojaat qiling!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        try:
            topic_id = request.query_params.get('lesson_room')
            group_id = request.query_params.get('group_id')
            bbb_id = request.query_params.get('bbb_id')

            if not group_id:
                return Response({'success': False, 'message': 'Guruh IDsi mavjud emas. Adminga murojaat qiling!'},
                                status=status.HTTP_404_NOT_FOUND)
            if not topic_id:
                return Response({'success': False, 'message': 'Mavzular IDsi mavjud emas. Adminga murojaat qiling!'},
                                status=status.HTTP_404_NOT_FOUND)
            if not bbb_id:
                return Response({'success': False, 'message': 'Bigbluebutton mavjud emas. Adminga murojaat qiling!'},
                                status=status.HTTP_404_NOT_FOUND)
            try:
                group = Group.objects.get(id=group_id)
                topic = LessonRoom.objects.get(id=topic_id)
                base_url = self.bbb_baseurl()
                room = self.find_room(bbb_id)
                if not self.room_status(base_url, room):

                    return Response({'success': False, 'message': 'Video dars hali boshlanmagan!, O`qituvchiga murojaat qiling!'},
                                    status=status.HTTP_400_BAD_REQUEST)

                user = request.user.student
                url = self.join_room(base_url, room, user)
                return Response({'success': True, 'url': url}, status=status.HTTP_200_OK)

            except Exception as ex:
                print(str(ex))
                return Response(
                    {'success': False, 'message': 'Tizimda muammo bor!'},
                    status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response(
                    {'success': False,'error': str(e)},status=status.HTTP_400_BAD_REQUEST
                )

        except ValueError as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            return Response({'success': False, 'message': 'Guruh topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        except LessonRoom.DoesNotExist:
            return Response({'success': False, 'message': 'Xona topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'message': f"Xatolik: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
