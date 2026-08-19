from rest_framework.views import APIView
from rest_framework.response import Response
from learning_process.models import Curriculum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
import datetime
from employee.models import Employee
from content.models import Content, Content_teacher, Topic, Video_content, File_content, Content_teacher, Task, \
    Task_students, Task_file
from drf_yasg.utils import swagger_auto_schema
from teacher.views import Check_teacher
from .serializers import TasksSerializer, ConnectGroupSerializers, StudentsSerializers, Task_GroupsSerializers, \
    Task_fileSerializers, CreateTaskWithGroupSerializers, ViewOneTask
from group.models import Group
from students.models import Student
from django.db import transaction
import json
import uuid


class GetTasksView(APIView):

    def get(self, request, *args, **kwargs):

        user = request.user
        teacher_id = user.employee.employee_id_number
        topic_id = self.request.query_params.get('topic_id')

        if topic_id is None:
            return Response({'errors': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        try:
            item = Topic.objects.get(id=topic_id)
        except item.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if teacher['check']:
            try:
                tasks = Task.objects.filter(topic_id_task=item, teacher_id=teacher['teacher'])
                obj = TasksSerializer(tasks, many=True)
                return Response({
                    'success': True,
                    'result': obj.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'succes': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class GetListGroupByTopic(APIView):
    def get(self, request, *args, **kwargs):
        topic_id = self.request.query_params.get('topic_id')
        user = request.user
        teacher_id = user.employee.employee_id_number
        if topic_id is None:
            return Response({'errors': 'topic_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            return Response({'errors': True, 'message': 'mavzu topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        try:
            connect_teacher = Content_teacher.objects.get(id=topic.content_teacher_connect.id)
        except Exception as e:
            return Response({'errors': True, 'message': 'mavzu topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                serializer = ConnectGroupSerializers(connect_teacher.group_by.all(), many=True)
                return Response({'succes': True, 'result': serializer.data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class GetListStudentbyTopic(APIView):
    def get(self, request, *args, **kwargs):
        group_id = self.request.query_params.get('group_id')
        user = request.user
        teacher_id = user.employee.employee_id_number
        if group_id is None:
            return Response({'errors': 'group_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        if teacher_id is None:
            return Response({'errors': 'teacher_id yuborilgan jsonda  mavjud emas'}, status=status.HTTP_404_NOT_FOUND)
        try:
            group = Group.objects.get(id=group_id)
        except Exception as e:
            return Response({'errors': True, 'message': 'Guruh topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        try:
            students = Student.objects.filter(group=group)
            print(students)
        except Exception as e:
            return Response({'errors': True, 'message': 'Guruh Birktrilgan talaba topilmadi', 'error_massage': str(e)},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                serializer = StudentsSerializers(students, many=True)
                return Response({'succes': True, 'result': serializer.data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'succes': False, 'teacher_status': teacher['check']}, status=status.HTTP_404_NOT_FOUND)


class CreateGroupTask(APIView):
    @swagger_auto_schema(request_body=CreateTaskWithGroupSerializers)
    def post(self, request, *args, **kwargs):
        if not request.FILES:
            return Response({'succes': False, 'message': 'Fayilar topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            tasks = CreateTaskWithGroupSerializers(data=request.data)
            if tasks.is_valid():
                task = Task()
                try:
                    topic = Topic.objects.get(id=tasks.validated_data['topic_id_task'])
                except Exception as e:
                    return Response({'succes': False, 'message': 'topic_id_task mavzu topilmadi'},
                                    status=status.HTTP_404_NOT_FOUND)
                task.topic_id_task = topic
                task.name = tasks.validated_data['name']
                task.comment = tasks.validated_data['comment']
                task.start_date = tasks.validated_data['start_date']
                task.end_date = tasks.validated_data['end_date']
                task.score = int(tasks.validated_data['score'])
                task.attempts = int(tasks.validated_data['attempts'])
                teacher = Check_teacher(tasks.validated_data['teacher_id'])
                if teacher['check']:
                    task.teacher_id = teacher['teacher']
                else:
                    return Response({'succes': False, 'teacher_status': teacher['check']},
                                    status=status.HTTP_404_NOT_FOUND)

            else:
                return Response(tasks.errors, status=status.HTTP_400_BAD_REQUEST)
            try:
                task.save()

            except Exception as e:
                transaction.set_rollback(True)
                return Response({'success': False, 'message': 'Task yartishda hatolik bor'},
                                status=status.HTTP_400_BAD_REQUEST)
            task_check = tasks.validated_data['task_check']
            if task_check:
                students_get = tasks.validated_data['task_student']
                for student in students_get:
                    try:
                        student = Student.objects.get(id=student)
                        try:
                            task_student = Task_students()
                            number = Task_students.objects.filter(task_student_id=student,
                                                                  tasks_id__topic_id_task=topic).count()
                            last_number = Task_students.objects.filter(task_student_id=student,
                                                                       tasks_id__topic_id_task=topic)
                            if number == 0:
                                number = 1
                                task_student.status_control = True
                            else:
                                number = number + 1
                                for task in last_number:
                                    if (not task.mark_status) and task.time_status:
                                        task_student.status_control = False
                                    else:
                                        task_student.status_control = True
                            task_student.task_check = task_check
                            task_student.task_group_id = student.group
                            task_student.task_student_id = student
                            task_student.tasks_id = task
                            task_student.teacher_id = teacher['teacher']
                            task_student.number = number
                            task_student.save()
                        except Exception as e:
                            transaction.set_rollback(True)
                            return Response(
                                {'success': False, 'message': 'Studentlarni birktrishda muamo bor !',
                                 'errors': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response(
                            {'success': False, 'message': 'Student bor!',
                             'errors': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
            else:
                groups = {}
                for i in tasks.validated_data['task_group']:
                    try:
                        group = Group.objects.get(id=i)
                        groups[group.name] = group
                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response({'success': False, 'message': 'Guruh topilmadi!', 'errors': str(e)},
                                        status=status.HTTP_400_BAD_REQUEST)
                students = {}
                try:
                    for group in groups.values():
                        student = Student.objects.filter(group=group)
                        students[group.name] = student
                except Exception as e:
                    transaction.set_rollback(True)
                    return Response({'success': False, 'message': 'Studentlar olishda muamo bor!', 'errors': str(e)},
                                    status=status.HTTP_400_BAD_REQUEST)
                for student in students.values():
                    for obj in student:
                        try:
                            number = Task_students.objects.filter(task_student_id=student,
                                                                  tasks_id__topic_id_task=topic).count()
                            if number == 0:
                                number = 1
                            else:
                                number = number + 1
                            task_student = Task_students()
                            task_student.task_check = task_check
                            task_student.task_group_id = obj.group
                            task_student.task_student_id = obj
                            task_student.tasks_id = task
                            task_student.teacher_id = teacher['teacher']
                            task_student.number = number
                            task_student.save()
                        except Exception as e:
                            transaction.set_rollback(True)
                            return Response(
                                {'success': False, 'message': 'Studentlarni birktrishda muamo bor!',
                                 'errors': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                files = request.FILES.getlist('task_files')
                # Process each file
                for file in files:
                    task_file = Task_file()
                    task_file.task_file = file
                    task_file.task = task
                    task_file.save()
            except Exception as e:
                transaction.set_rollback(True)
                return Response(
                    {'success': False, 'message': 'Fayil birktrishda muamo bor!',
                     'errors': str(e)},
                    status=status.HTTP_400_BAD_REQUEST)

        return Response({'succes': True, 'message': 'Topshiriq qo`shildi!'}, status=status.HTTP_201_CREATED)


class GetOneTask(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(id=pk)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        teacher_id = user.employee.employee_id_number
        if teacher_id is None:
            return Response({'success': False, 'message': 'O`qtuvchi id kirtish majburiy'},
                            status=status.HTTP_404_NOT_FOUND)
        teacher = Check_teacher(teacher_id)
        if teacher['check']:
            try:
                serializer = ViewOneTask(task, many=True)
                return Response({'success':True,'message':'','results':serializer.data},status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'success': False, 'message': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'message': teacher['check']},
                            status=status.HTTP_404_NOT_FOUND)

class UpdateTask(APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(id=pk)
        except Exception as e:
            return Response({'success':False,'message':'Topshiriq topilmadi!'})

        return Response({'success':True,'resutls':'Baza'},status=status.HTTP_200_OK)
