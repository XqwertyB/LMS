from django.db.models import Q
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from config.permissions import AllowOnlyTrustedOrigins
from semestr.models import Hsemester_action
from shared.permissions import IsAdminTeacherOrStudent, IsAdmin
from .serializers import SubjectCreateSerializer, SubjectgroupSerializer, SubjectSerializer, Subject_blockSerializer, \
    Subject_typeSerializer, Subject_exam_finishSerializer, Subject_CurriculumSerializer
from .models import Subject, Subjectgroup, Subject_exam_finish, Subject_block, Subject_type, Subject_Curriculum


class SubjectgroupcreateList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]
    queryset = Subjectgroup.objects.filter(status_action=True)
    serializer_class = SubjectgroupSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class SubjectgroupupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    queryset = Subjectgroup.objects.filter(status_action=True)
    serializer_class = SubjectgroupSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SubjectgroupGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]

    def get(self, request, pk):
        try:
            obj = Subjectgroup.objects.get(id=pk)
            serializer = SubjectgroupSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Subjectgroupedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request):
        # Handle GET request
        obj = Subjectgroup.objects.filter(status_action=False)
        serializer = SubjectgroupSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Subjectgroup.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class SubjectcreateList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]
    queryset = Subject.objects.filter(status_action=True)
    serializer_class = SubjectCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class SubjectupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    queryset = Subject.objects.filter(status_action=True)
    serializer_class = SubjectCreateSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SubjectGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]

    def get(self, request, pk):
        try:
            obj = Subject.objects.get(id=pk)
            serializer = SubjectSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Subjectdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request):
        # Handle GET request
        obj = Subject.objects.filter(status_action=False)
        serializer = SubjectSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Subject.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Subject_blockcreateList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]
    queryset = Subject_block.objects.filter(status_action=True)
    serializer_class = Subject_blockSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class Subject_blockupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    queryset = Subject_block.objects.filter(status_action=True)
    serializer_class = Subject_blockSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class Subject_blockGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]

    def get(self, request, pk):
        try:
            obj = Subject_block.objects.get(id=pk)
            serializer = Subject_blockSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Subject_blockdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request):
        # Handle GET request
        obj = Subject_block.objects.filter(status_action=False)
        serializer = Subject_blockSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Subject_block.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Subject_typecreateList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]
    queryset = Subject_type.objects.filter(status_action=True)
    serializer_class = Subject_typeSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class Subject_typeupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]
    queryset = Subject_type.objects.filter(status_action=True)
    serializer_class = Subject_typeSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class Subject_typeGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]

    def get(self, request, pk):
        try:
            obj = Subject_type.objects.get(id=pk)
            serializer = Subject_typeSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Subject_typedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request):
        # Handle GET request
        obj = Subject_type.objects.filter(status_action=False)
        serializer = Subject_typeSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Subject_type.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Subject_exam_finishcreateList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]
    queryset = Subject_exam_finish.objects.filter(status_action=True)
    serializer_class = Subject_exam_finishSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class Subject_exam_finishupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]
    queryset = Subject_exam_finish.objects.filter(status_action=True)
    serializer_class = Subject_exam_finishSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class Subject_exam_finishGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent, ]

    def get(self, request, pk):
        try:
            obj = Subject_exam_finish.objects.get(id=pk)
            serializer = Subject_exam_finishSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Subject_exam_finishdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request):
        # Handle GET request
        obj = Subject_exam_finish.objects.filter(status_action=False)
        serializer = Subject_exam_finishSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Subject_exam_finish.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


#
# class SubjectsListApiView(generics.RetrieveAPIView):
#     permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
#     serializer_class = Subject_CurriculumSerializer
#     lookup_field = ['curriculum_id', 'semester_id']
#
#     def get_queryset(self):
#         curriculum_id = self.kwargs.get(self.lookup_field[0])
#         semester_id = self.kwargs.get(self.lookup_field[1])
#         queryset = Subject_Curriculum.objects.filter((
#                 Q(subject_curriculum_id=curriculum_id) & Q(subject_semestr_id=semester_id)
#         ))
#         return queryset
#
#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         if queryset.exists():
#             serializer = self.get_serializer(queryset, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             response_data = {
#                 "status": False,
#                 "message": "Ushbu o'quv rejaga tegishli fanlar topilmadi..."
#             }
#             return Response(response_data, status=status.HTTP_404_NOT_FOUND)
class SubjectsListApiView(generics.RetrieveAPIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdminTeacherOrStudent]
    serializer_class = Subject_CurriculumSerializer

    def get_queryset(self):
        curriculum_id = self.kwargs.get('curriculum_id')

        current_semester = Hsemester_action.objects.filter(
            curriculum_id=curriculum_id,
            current=True
        ).select_related('semester').first()

        if not current_semester:
            return Subject_Curriculum.objects.none()

        semester_id = current_semester.semester_id

        queryset = Subject_Curriculum.objects.filter(
            subject_curriculum_id=curriculum_id,
            subject_semestr_id=semester_id
        )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Ushbu o'quv rejaga tegishli fanlar topilmadi..."
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
