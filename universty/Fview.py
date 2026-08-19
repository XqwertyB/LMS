from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdminTeacherOrStudent,IsAdmin
from .serializers import Faculty_typeSerializer, FacultySerializer, DepartmentSerializer, SectionSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import Faculty, Faculty_type, Department, Section
from rest_framework.views import APIView
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .filters import FacultyFilter, DepartmentFilter


class Faculty_typelist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = Faculty_type.objects.filter(status_action=True)
    serializer_class = Faculty_typeSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class Faculty_typeupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Faculty_type.objects.filter(status_action=True)
    serializer_class = Faculty_typeSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class Faculty_typeGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self, request, pk):
        try:
            obj = Faculty_type.objects.get(id=pk)
            serializer = Faculty_typeSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Faculty_typedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = Faculty_type.objects.filter(status_action=False)
        serializer = Faculty_typeSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Faculty_type.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class Facultylist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = Faculty.objects.filter(status_action=True)
    serializer_class = FacultySerializer
    filterset_class = FacultyFilter

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class FacultyupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Faculty.objects.filter(status_action=True)
    serializer_class = FacultySerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class FacultyGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self, request, pk):
        try:
            obj = Faculty.objects.get(id=pk)
            serializer = FacultySerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Facultydelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = Faculty.objects.filter(status_action=False)
        serializer = FacultySerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Faculty.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class Departmentlist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = Department.objects.filter(status_action=True)
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DepartmentFilter

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class DepartmentupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Department.objects.filter(status_action=True)
    serializer_class = DepartmentSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class DepartmentGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self, request, pk):
        try:
            obj = Department.objects.get(id=pk)
            serializer = DepartmentSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Departmentdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = Department.objects.filter(status_action=False)
        serializer = DepartmentSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Department.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class Sectionlist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = Section.objects.filter(status_action=True)
    serializer_class = SectionSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class SectionupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Section.objects.filter(status_action=True)
    serializer_class = SectionSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SectionGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self, request, pk):
        try:
            obj = Section.objects.get(id=pk)
            serializer = SectionSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Sectiondelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = Section.objects.filter(status_action=False)
        serializer = SectionSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Section.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
