from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdminTeacherOrStudent,IsAdmin
from .serializers import BspecialitySerializer, MspecialitySerializer, OspecialitySerializer
from .models import Bspeciality, Mspeciality, Ospeciality


class BspecialityList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    queryset = Bspeciality.objects.filter(status_action=True)
    serializer_class = BspecialitySerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class BspecialityupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Bspeciality.objects.filter(status_action=True)
    serializer_class = BspecialitySerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class BspecialityGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Bspeciality.objects.get(id=pk)
            serializer = BspecialitySerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Bspecialitydelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Bspeciality.objects.filter(status_action=False)
        serializer = BspecialitySerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Bspeciality.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class MspecialityList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Mspeciality.objects.filter(status_action=True)
    serializer_class = MspecialitySerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class MspecialityupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Mspeciality.objects.filter(status_action=True)
    serializer_class = MspecialitySerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class MspecialityGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Mspeciality.objects.get(id=pk)
            serializer = MspecialitySerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Mspecialitydelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Mspeciality.objects.filter(status_action=False)
        serializer = MspecialitySerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Mspeciality.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class OspecialityList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Ospeciality.objects.filter(status_action=True)
    serializer_class = OspecialitySerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class OspecialityupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Ospeciality.objects.filter(status_action=True)
    serializer_class = OspecialitySerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OspecialityGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Ospeciality.objects.get(id=pk)
            serializer = OspecialitySerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Ospecialitydelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Ospeciality.objects.filter(status_action=False)
        serializer = OspecialitySerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Ospeciality.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
