from rest_framework.views import APIView
from rest_framework.response import Response

from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdmin, IsAdminOrTeacher
from subjects.models import Subject_Curriculum, Subject
from .serializers import ContentViewSerializer, Content_teacherViewSerializer, RoletypeViewSerializer, \
    RoletypeCreateSerializer, Content_teacherCreateSerializer, Task_typeViewSerializer, Task_typeCreateSerializer, \
    Content_countSerializer, Content_teacherSerializerdetect_subject, TrainingTypeSeralizerInfo, \
    Content_teacherSerializerUpdate
from .models import Content, Content_teacher, Roletype, Task_type, Topic, Video_content, Task
from semestr.models import Hsemester_action, Hsemester
from group.models import Group
import datetime
from learning_process.models import Curriculum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from django.db.models import Count, Q, Prefetch
from group.serializers import GroupViewSerializer
from django.db import transaction
from shared.utils import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated
from shared.models import TrainingType
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class   Subject_Content_IN_SYSTEM_Active(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, *args, **kwargs):
        active_content = Hsemester_action.objects.filter(current=True)
        start_time = datetime.datetime.now()
        for obj in active_content:
            subject_curl = Subject_Curriculum.objects.filter(
                Q(subject_semestr=obj.semester) & Q(subject_curriculum=obj.curriculum))
            for xojb in subject_curl:
                if xojb.ratingGrade.code == '11':
                    if xojb.subject_semestr == obj.semester:
                        with transaction.atomic():
                            try:
                                if not Content.objects.filter(hemis_id=xojb.hemis_id).exists():
                                    content = Content()
                                    content.hemis_id = xojb.hemis_id
                                    content.subject_id = xojb.subject
                                    content.curriculum_id = xojb.subject_curriculum
                                    content.semestr_action = obj.current
                                    content.content_semestrs = xojb.subject_semestr
                                    content.credit = xojb.credit
                                    jn = 0
                                    on = 0
                                    yn = 0
                                    for ball in xojb.sub_exam_type.all():
                                        if ball.examType.code in ['12', '17', '18']:
                                            on = on + ball.max_ball
                                        if ball.examType.code == '13':
                                            yn = yn + ball.max_ball
                                        if ball.examType.code in ['11', '16', '15']:
                                            jn = jn + ball.max_ball
                                    content.totatl_score_jn = jn
                                    content.totatl_score_on = on
                                    content.totatl_score_yn = yn
                                    content.level = obj.level
                                    groups = Group.objects.filter(group_curriculum=xojb.subject_curriculum)
                                    content.save()
                                    for group in groups:
                                        content.group.add(group)
                                    content.save()
                                else:
                                    content = Content.objects.get(hemis_id=xojb.hemis_id)
                                    content.subject_id = xojb.subject
                                    content.curriculum_id = xojb.subject_curriculum
                                    content.semestr_action = obj.current
                                    content.content_semestrs = xojb.subject_semestr
                                    content.credit = xojb.credit
                                    jn = 0
                                    on = 0
                                    yn = 0
                                    for ball in xojb.sub_exam_type.all():
                                        if ball.examType.code in ['12','17','18']:
                                            on = on + ball.max_ball
                                        if ball.examType.code == '13':
                                            yn = yn + ball.max_ball
                                        if ball.examType.code in ['11','16','15']:
                                            jn = jn + ball.max_ball
                                    content.totatl_score_jn = jn
                                    content.totatl_score_on = on
                                    content.totatl_score_yn = yn
                                    content.level = obj.level
                                    groups = Group.objects.filter(group_curriculum=xojb.subject_curriculum)
                                    content.save()
                                    for group in content.group.all():
                                        content.group.remove(group)
                                    for group in groups:
                                        content.group.add(group)
                                    content.save()
                            except Exception as ex:
                                transaction.set_rollback(True)
                                return Response({'success': False,
                                                 'message': 'Fanlarni genertasiya qilishda muamo mavjud!'
                                                 })
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'success': True, 'time': elapsed_time})


class Subject_Content_IN_SYSTEM_Inactive(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, *args, **kwargs):
        active_content = Hsemester_action.objects.filter(current=False)
        start_time = datetime.datetime.now()
        for obj in active_content:
            subject_curl = Subject_Curriculum.objects.filter(
                Q(subject_semestr=obj.semester) and Q(subject_curriculum=obj.curriculum))
            for xojb in subject_curl:
                if xojb.ratingGrade.code == '11':
                    if xojb.subject_semestr == obj.semester:
                        with transaction.atomic():
                            try:
                                if not Content.objects.filter(hemis_id=xojb.hemis_id).exists():
                                    content = Content()
                                    content.hemis_id = xojb.hemis_id
                                    content.subject_id = xojb.subject
                                    content.curriculum_id = xojb.subject_curriculum
                                    content.semestr_action = obj.current
                                    content.content_semestrs = xojb.subject_semestr
                                    content.credit = xojb.credit
                                    jn = 0
                                    on = 0
                                    yn = 0
                                    for ball in xojb.sub_exam_type.all():
                                        if ball.examType.code in ['12', '17', '18']:
                                            on = on + ball.max_ball
                                        if ball.examType.code == '13':
                                            yn = yn + ball.max_ball
                                        if ball.examType.code in ['11', '16', '15']:
                                            jn = jn + ball.max_ball
                                    content.totatl_score_jn = jn
                                    content.totatl_score_on = on
                                    content.totatl_score_yn = yn
                                    content.level = obj.level
                                    groups = Group.objects.filter(group_curriculum=xojb.subject_curriculum)
                                    content.save()
                                    for group in groups:
                                        content.group.add(group)
                                    content.save()
                                else:
                                    content = Content.objects.get(hemis_id=xojb.hemis_id)
                                    content.subject_id = xojb.subject
                                    content.curriculum_id = xojb.subject_curriculum
                                    content.semestr_action = obj.current
                                    content.content_semestrs = xojb.subject_semestr
                                    content.credit = xojb.credit
                                    jn = 0
                                    on = 0
                                    yn = 0
                                    for ball in xojb.sub_exam_type.all():
                                        if ball.examType.code in ['12', '17', '18']:
                                            on = on + ball.max_ball
                                        if ball.examType.code == '13':
                                            yn = yn + ball.max_ball
                                        if ball.examType.code in ['11', '16', '15']:
                                            jn = jn + ball.max_ball
                                    content.totatl_score_jn = jn
                                    content.totatl_score_on = on
                                    content.totatl_score_yn = yn
                                    content.level = obj.level
                                    groups = Group.objects.filter(group_curriculum=xojb.subject_curriculum)
                                    content.save()
                                    for group in content.group.all():
                                        content.group.remove(group)
                                    for group in groups:
                                        content.group.add(group)
                                    content.save()
                            except Exception as ex:
                                transaction.set_rollback(True)
                                return Response({'success': False,
                                                 'message': 'Fanlarni genertasiya qilishda muamo mavjud!'
                                                 })
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        return Response({'success': True, 'time': elapsed_time})


# Filterlar imkoni Contentni oquv yili va semestr Fan bo`yicha
class ContentAllView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    pagination_class = CustomPageNumberPagination
    serializer_class = ContentViewSerializer

    @swagger_auto_schema(
        operation_description="📚 Content ro‘yxatini olish",
        tags=["Content"],
        manual_parameters=[
            openapi.Parameter("curriculum_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("name", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("educationyear_code", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("educationtype_code", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("educationform_code", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("semestrs_code", openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        responses={200: ContentViewSerializer(many=True)}
    )
    def get(self, request, format=None):
        try:
            queryset = Content.objects.filter(
                status_action=True,
                semestr_action=True
            ).prefetch_related(
                Prefetch(
                    "curriculum_id",
                    queryset=Curriculum.objects.select_related(
                        "educationyear",
                        "educationtype",
                        "educationform"
                    )
                )
            )

            curriculum_id = request.query_params.get("curriculum_id")
            name = request.query_params.get("name")
            educationyear = request.query_params.get("educationyear_code")
            educationtype = request.query_params.get("educationtype_code")
            educationform = request.query_params.get("educationform_code")
            content_semestrs = request.query_params.get("semestrs_code")

            if curriculum_id:
                queryset = queryset.filter(curriculum_id=curriculum_id)

            if content_semestrs:
                queryset = queryset.filter(content_semestrs__code=content_semestrs)

            if name:
                queryset = queryset.filter(curriculum_id__name__icontains=name)

            if educationyear:
                queryset = queryset.filter(curriculum_id__educationyear__code=educationyear)

            if educationtype:
                queryset = queryset.filter(curriculum_id__educationtype__code=educationtype)

            if educationform:
                queryset = queryset.filter(curriculum_id__educationform__code=educationform)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {"errors": True, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        # return Response(seralizer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        curriculum = False
        subject = False
        content_semestr = False
        if 'curriculum_id' in request.data:
            curriculum = True
        if 'subject_id' in request.data:
            subject = True
        if 'content_semestrs' in request.data:
            content_semestr = True
        if curriculum and subject and content_semestr:
            if not request.data['curriculum_id']:
                return Response({'error': 'Oquv bo`lim topilmagan!'})
            if not request.data['subject_id']:
                return Response({'error': 'Fani topilmagan!'})
            if not request.data['content_semestrs']:
                return Response({'error': 'Semestr topilmagan!'})
            try:
                sem = Hsemester.objects.get(id=request.data['content_semestrs'])
            except:
                return Response({'error': 'Semestr topilmagan!'})
            try:
                sub = Subject.objects.get(id=request.data['subject_id'])
            except:
                return Response({'error': 'Fani topilmagan!'})
            try:
                cur = Curriculum.objects.get(id=request.data['curriculum_id'])
            except:
                return Response({'error': 'Oquv bo`lim topilmagan!'})
            obj = Content.objects.filter(status_action=True, curriculum_id=cur, subject_id=sub, content_semestrs=sem)
            seralizer = ContentViewSerializer(obj, many=True)
            return Response(seralizer.data)
        elif curriculum and subject and not content_semestr:
            if not request.data['curriculum_id']:
                return Response({'error': 'Oquv bo`lim topilmagan!'})
            if not request.data['subject_id']:
                return Response({'error': 'Fani topilmagan!'})
            try:
                sub = Subject.objects.get(id=request.data['subject_id'])
            except:
                return Response({'error': 'Fani topilmagan!'})
            try:
                cur = Curriculum.objects.get(id=request.data['curriculum_id'])
            except:
                return Response({'error': 'Oquv bo`lim topilmagan!'})
            obj = Content.objects.filter(status_action=True, curriculum_id=cur, subject_id=sub)
            seralizer = ContentViewSerializer(obj, many=True)
            return Response(seralizer.data)
        elif curriculum and not subject and not content_semestr:
            if not request.data['curriculum_id']:
                return Response({'error': 'Oquv bo`lim topilmagan!'})
            try:
                cur = Curriculum.objects.get(id=request.data['curriculum_id'])
            except:
                return Response({'error': 'Oquv bo`lim topilmagan!'})
            obj = Content.objects.filter(status_action=True, curriculum_id=cur)
            seralizer = ContentViewSerializer(obj, many=True)
            return Response(seralizer.data)
        else:
            obj = Content.objects.filter(status_action=True)
            seralizer = ContentViewSerializer(obj, many=True)
            return Response(seralizer.data)


class Writescore(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAuthenticated, ]

    def post(self, request, format=None):
        if not 'id' in request.data:
            return Response({'error': 'id kirtilmagan!'})
        if not 'totatl_score_jn' in request.data:
            return Response({'error': 'totatl_score_jn kirtilmagan!'})
        if not 'totatl_score_on' in request.data:
            return Response({'error': 'totatl_score_on kirtilmagan!'})
        if not 'totatl_score_yn' in request.data:
            return Response({'error': 'totatl_score_yn kirtilmagan!'})
        if not request.data['id']:
            return Response({'error': 'id qiymat mavjud emas!'})
        if not request.data['totatl_score_jn']:
            try:
                if not int(request.data['totatl_score_jn']) == 0:
                    return Response({'error': 'totatl_score_jn qiymat mavjud emas!'})
            except:
                return Response({'errors': 'kirtilgan qiymatlar butun emas!'})
        if not request.data['totatl_score_on']:
            try:
                if not int(request.data['totatl_score_on']) == 0:
                    return Response({'error': 'totatl_score_on qiymat mavjud emas!'})

            except:
                return Response({'errors': 'kirtilgan qiymatlar butun emas!'})
        if not request.data['totatl_score_yn']:
            try:
                if not int(request.data['totatl_score_yn']) == 0:
                    return Response({'error': 'totatl_score_yn qiymat mavjud emas!'})

            except:
                return Response({'errors': 'kirtilgan qiymatlar butun emas!'})
        totatl_score_jn = int(request.data['totatl_score_jn'])
        totatl_score_on = int(request.data['totatl_score_on'])
        totatl_score_yn = int(request.data['totatl_score_yn'])
        sum = totatl_score_jn + totatl_score_on + totatl_score_yn
        if sum == 100:
            try:
                obj = Content.objects.get(id=request.data['id'])
            except:
                return Response({'errors': 'id topilmadi'})
            obj.totatl_score_jn = totatl_score_jn
            obj.totatl_score_on = 100 - totatl_score_yn
            obj.totatl_score_jn = totatl_score_yn
            obj.save()
            return Response({'success': 'True'})
        else:
            return Response({'errors': 'Ballar taqsimot to`giri emas!'})


class Content_teacherView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAuthenticated, ]

    def post(self, request, format=None):
        if not 'id' in request.data:
            return Response({'error': 'id kirtilmagan!'})
        if not request.data['id']:
            return Response({'error': 'id qiymat mavjud emas!'})
        try:
            content = Content.objects.get(id=request.data['id'])
        except:
            return Response({'errors': 'Bu tizimda mavjud emas!'})

        obj = Content_teacher.objects.filter(content_id=content)
        serializer_data = Content_teacherViewSerializer(obj, many=True)
        return Response({'rezults': serializer_data.data})


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Role_typeList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAuthenticated, ]
    queryset = Roletype.objects.filter(status_action=True)
    serializer_class = RoletypeCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class RoletypeupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAuthenticated, ]
    queryset = Roletype.objects.filter(status_action=True)
    serializer_class = RoletypeCreateSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class RoletypeGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAuthenticated, ]

    def get(self, request, pk):
        try:
            obj = Roletype.objects.get(id=pk)
            serializer = RoletypeViewSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Roletypedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAuthenticated, ]

    def get(self, request):
        # Handle GET request
        obj = Roletype.objects.filter(status_action=False)
        serializer = RoletypeViewSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Roletype.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Content_teacherList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    queryset = Content_teacher.objects.filter(status_action=True)
    serializer_class = Content_teacherCreateSerializer

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except Exception as ex:
            raise Response({'error': True, 'message': str(ex)})

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


# class Content_teacherupdateAPIView(generics.UpdateAPIView):
#     queryset = Content_teacher.objects.filter(status_action=True)
#     serializer_class = Content_teacherCreateSerializer
#
#     def patch(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)


class Content_teacherGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request, pk):
        try:
            obj = Content_teacher.objects.get(id=pk)
            serializer = Content_teacherViewSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Content_teacherdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request):
        # Handle GET request
        obj = Content_teacher.objects.filter(status_action=False)
        serializer = Content_teacherViewSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Content_teacher.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class Content_group_view(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def post(self, request, *args, **kwargs):
        content = request.data.get('content', None)
        lang = request.data.get('lang', None)
        if content is None:
            return Response({'errors': 'content yuborilgan jsonda  mavjud emas'})
        try:
            obj = Content.objects.get(id=content)
        except Exception as e:
            return Response({'success': False, 'message': str(e)})
        if lang is None:
            group = obj.group.all()
        else:
            group = obj.group.all().filter(educationLang__id=lang)
        try:
            serializer = GroupViewSerializer(group, many=True)
            return Response({'success': True,
                             'result': serializer.data})
        except Exception as e:
            return Response({'success': False, 'message': str(e)})


class Task_typeList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    queryset = Task_type.objects.filter(status_action=True)
    serializer_class = Task_typeCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class Task_typeupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    queryset = Roletype.objects.filter(status_action=True)
    serializer_class = Task_typeCreateSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class Task_typeGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request, pk):
        try:
            obj = Task_type.objects.get(id=pk)
            serializer = Task_typeViewSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Task_typedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request):
        # Handle GET request
        obj = Task_type.objects.filter(status_action=False)
        serializer = Task_typeViewSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Task_type.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ContentCount(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request, *args, **kwargs):
        content_teacher_connect = self.request.query_params.get('content_teacher_connect')
        if content_teacher_connect is None:
            return Response({'errors': True, 'message': 'Topilmadi!'}, status=status.HTTP_403_FORBIDDEN)
        try:
            content_conect = Content_teacher.objects.get(id=content_teacher_connect)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_403_FORBIDDEN)
        try:
            maruzalar = Topic.objects.filter(content_teacher_connect=content_conect, status_action=True)
            maruza_cunt = maruzalar.count()
            video_count = 0
            task_count = 0
            for i in maruzalar:
                video_content = Video_content.objects.filter(video_id_topic=i).count()
                video_count += video_content
                task_content = Task.objects.filter(topic_id_task=i).count()
                task_count += task_content
            data = {
                'maruza': maruza_cunt,
                'video': video_count,
                'topshiriq': task_count
            }
            conunt = Content_countSerializer(data=data)
            if conunt.is_valid():
                return Response({'sucees': True, 'results': conunt.data}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': True, 'message': 'str(e)'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_403_FORBIDDEN)


class Content_teacher_subjectView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    serializer_class = Content_teacherSerializerdetect_subject

    def get(self, request, pk):
        try:
            obj = Content.objects.get(id=pk)
        except Content.DoesNotExist:
            return Response({'errors': True, 'message': "Content topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
        try:
            content_teacher = Content_teacher.objects.filter(content_id=obj)

            # Serializer orqali ma'lumotlarni oling
            serializer = self.serializer_class(content_teacher, many=True)

        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Paginationdan foydalanmasdan natijalarni qaytarish
        return Response(serializer.data, status=status.HTTP_200_OK)


# class Content_teacher_edite(APIView):
#     permission_classes = [IsAuthenticated, ]
class GetTrainingTypeView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    def get(self, request):
        try:
            t_type = TrainingType.objects.filter(status_action=True)
            seralizer = TrainingTypeSeralizerInfo(t_type, many=True)
            return Response({
                'results': seralizer.data,
            }, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({
                'error': True,
                'message': str(ex)
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangeTrainingType_Content(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]

    @swagger_auto_schema(
        operation_description="Content_teacher ning training_type maydonini yangilash",
        responses={
            200: Content_teacherSerializerUpdate,
            404: openapi.Response(description="Topilmadi", examples={
                "application/json": {"error": True, "message": "Bu yuborilgan id mavjud emas!"}}),
            400: openapi.Response(description="Notog'ri ma'lumot",
                                  examples={"application/json": {"error": True, "message": "Some validation errors"}})
        },
        request_body=Content_teacherSerializerUpdate
    )
    def patch(self, request, pk):
        try:
            content_teacher = Content_teacher.objects.get(pk=pk)
        except Content_teacher.DoesNotExist:
            return Response({'error': True, 'message': 'Bu yuborilgan id mavjud emas!'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = Content_teacherSerializerUpdate(
            content_teacher,
            data=request.data,
            partial=True  # Qisman yangilash uchun partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'error': True, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DeleteContentTeacher(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def delete(self, request, pk):
        try:

            content_teacher = Content_teacher.objects.get(pk=pk)
        except Content_teacher.DoesNotExist:
            return Response(
                {'error': True, 'message': 'Bu yuborilgan id mavjud emas!'},
                status=status.HTTP_404_NOT_FOUND
            )
        content_teacher.delete()
        return Response(
            {'message': 'Content_teacher muvaffaqiyatli o\'chirildi!'},
            status=status.HTTP_204_NO_CONTENT
        )
