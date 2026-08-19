from django.db.models import F, Value
from django.db.models.functions import Greatest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdmin,IsAdminTeacherOrStudent
from shared.utils import CustomPageNumberPagination
from .serializers import EducationyearSerializer, EducationtypeSerializer, EducationformSerializer, \
    CurriculumSerializer, MarkingSystemSerializer, Science_branchSerializer, EducationlangSerializer, \
    GetCurriculumOneSerializer
from .models import Educationyear, Educationtype, Educationform, Curriculum, MarkingSystem, Science_branch, \
    Educationlang
from .filters import CurriculumFilter
from content.models import Content


# +
class EducationyearList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Educationyear.objects.filter(status_action=True).order_by('code')
    serializer_class = EducationyearSerializer
    pagination_class = CustomPageNumberPagination

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        current_year = self.queryset.filter(current=True).first()
        if not current_year:
            return Response([], status=status.HTTP_200_OK)

        years_around_current = self.queryset.filter(
            code__gte=int(current_year.code) - 4,
            code__lte=int(current_year.code) + 4
        ).order_by("code")

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(years_around_current, request, view=self)

        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class EducationyearupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Educationyear.objects.filter(status_action=True)
    serializer_class = EducationyearSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class EducationyearGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    def get(self, request, pk):
        try:
            obj = Educationyear.objects.get(id=pk)
            serializer = EducationyearSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Educationyeardelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Educationyear.objects.filter(status_action=False)
        serializer = EducationyearSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Educationyear.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +
class EducationtypeList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Educationtype.objects.filter(status_action=True)
    serializer_class = EducationtypeSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class EducationtypeupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Educationtype.objects.filter(status_action=True)
    serializer_class = EducationtypeSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class EducationtypeGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Educationtype.objects.get(id=pk)
            serializer = EducationtypeSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Educationtypedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Educationtype.objects.filter(status_action=False)
        serializer = EducationtypeSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Educationtype.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +
class EducationformList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Educationform.objects.filter(status_action=True)
    serializer_class = EducationformSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class EducationformupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Educationform.objects.filter(status_action=True)
    serializer_class = EducationformSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class EducationformGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Educationform.objects.get(id=pk)
            serializer = EducationformSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Educationformdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Educationform.objects.filter(status_action=False)
        serializer = EducationformSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Educationform.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +
class MarkingSystemList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = MarkingSystem.objects.filter(status_action=True)
    serializer_class = MarkingSystemSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class MarkingSystemupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = MarkingSystem.objects.filter(status_action=True)
    serializer_class = MarkingSystemSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class MarkingSystemGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = MarkingSystem.objects.get(id=pk)
            serializer = MarkingSystemSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class MarkingSystemdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = MarkingSystem.objects.filter(status_action=False)
        serializer = MarkingSystemSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = MarkingSystem.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +
class CurriculumList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Curriculum.objects.filter(status_action=True)
    serializer_class = CurriculumSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CurriculumFilter

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class CurriculumupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = MarkingSystem.objects.filter(status_action=True)
    serializer_class = MarkingSystemSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CurriculumGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Curriculum.objects.get(id=pk)
            serializer = CurriculumSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Curriculumdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Curriculum.objects.filter(status_action=False)
        serializer = CurriculumSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Curriculum.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +
class Science_branchList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Science_branch.objects.filter(status_action=True)
    serializer_class = Science_branchSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class Science_branchupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Science_branch.objects.filter(status_action=True)
    serializer_class = Science_branchSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class Science_branchGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Science_branch.objects.get(id=pk)
            serializer = Science_branchSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Science_branchdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Science_branch.objects.filter(status_action=False)
        serializer = Science_branchSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Science_branch.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +
class EducationlangList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Educationlang.objects.filter(status_action=True)
    serializer_class = EducationlangSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class EducationlangupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Educationlang.objects.filter(status_action=True)
    serializer_class = EducationlangSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class EducationlangGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Educationlang.objects.get(id=pk)
            serializer = EducationlangSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Educationlangdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Educationlang.objects.filter(status_action=False)
        serializer = EducationlangSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Educationlang.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class GetCurriculumOne(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAuthenticated, ]

    def get(self, request, pk):
        try:
            content = Content.objects.get(id=pk)
            seralizer = GetCurriculumOneSerializer(content, many=False)
            return Response({"success": True, "rezults": seralizer.data}, status=status.HTTP_200_OK)
        except Curriculum.DoesNotExist:
            return Response(
                {"error": True, 'message': "O`quv reja topilmadi."}, status=status.HTTP_404_NOT_FOUND
            )
