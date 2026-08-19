from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdminTeacherOrStudent, IsAdmin
from .models import ConnectSpeciality
from .serializers import ConnectSpecialitySerializer
from django_filters.rest_framework import DjangoFilterBackend


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class ConnectSpecialityList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    queryset = ConnectSpeciality.objects.filter(status_action=True)
    serializer_class = ConnectSpecialitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'bachelorSpecialty', 'masterSpecialty', 'doctorateSpecialty',
                        'ordinatureSpecialty', 'localitytype', 'educationtype', 'code']

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class ConnectSpecialityupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = ConnectSpeciality.objects.filter(status_action=True)
    serializer_class = ConnectSpecialitySerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ConnectSpecialityGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = ConnectSpeciality.objects.get(id=pk)
            serializer = ConnectSpecialitySerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class ConnectSpecialitydelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = ConnectSpeciality.objects.filter(status_action=False)
        serializer = ConnectSpecialitySerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = ConnectSpeciality.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
