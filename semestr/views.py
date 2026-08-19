from django.db.models import Q
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdminTeacherOrStudent, IsAdmin
from .serializers import HCourseSerializer, HsemesterSerializer, Hsemester_actionSerializer, \
    GetHsemester_actionSerializer
from .models import HCourse, Hsemester, Hsemester_action


class HCourseList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    queryset = HCourse.objects.filter(status_action=True)
    serializer_class = HCourseSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class HCourseupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = HCourse.objects.filter(status_action=True)
    serializer_class = HCourseSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HCourseGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = HCourse.objects.get(id=pk)
            serializer = HCourseSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class HCoursedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = HCourse.objects.filter(status_action=False)
        serializer = HCourseSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = HCourse.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class HsemesterList(generics.ListCreateAPIView):
    queryset = Hsemester.objects.filter(status_action=True)
    serializer_class = HsemesterSerializer
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class HsemesterupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Hsemester.objects.filter(status_action=True)
    serializer_class = HsemesterSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HsemesterGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Hsemester.objects.get(id=pk)
            serializer = HsemesterSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Hsemesterdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Hsemester.objects.filter(status_action=False)
        serializer = HsemesterSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Hsemester.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Hsemester_actionList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Hsemester_action.objects.filter(status_action=True)
    serializer_class = Hsemester_actionSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class Hsemester_actionupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Hsemester_action.objects.filter(status_action=True)
    serializer_class = Hsemester_actionSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class Hsemester_actionGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Hsemester_action.objects.get(id=pk)
            serializer = Hsemester_actionSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Hsemester_actiondelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Hsemester_action.objects.filter(status_action=False)
        serializer = Hsemester_actionSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Hsemester_action.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class SmesterCurrListApiView(generics.RetrieveAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    serializer_class = GetHsemester_actionSerializer
    lookup_field = 'curriculum_id'

    def get_queryset(self):
        curriculum_id = self.kwargs.get(self.lookup_field)
        queryset = Hsemester_action.objects.filter((
                Q(curriculum_id=curriculum_id) & Q(current=True)
        ))
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "status": False,
                "message": "Ushbu o'quv rejaga tegishli smesterlar topilmadi..."
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
