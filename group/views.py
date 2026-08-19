from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdminTeacherOrStudent,IsAdmin
from shared.utils import CustomPageNumberPagination
from .filters import GroupListFilter
from .models import Group
from .serializers import GroupSerializer, GroupViewSerializer


class GroupList(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent,]
    queryset = Group.objects.filter(status_action=True)
    serializer_class = GroupSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class GroupupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    queryset = Group.objects.filter(status_action=True)
    serializer_class = GroupSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GroupGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    def get(self, request, pk):
        try:
            obj = Group.objects.get(id=pk)
            serializer = GroupSerializer(obj, many=False)
            return Response(serializer.data)
        except:
            return Response({'error': 'Bu ko`rinshdagi obekt yo`q'})


class Groupdelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    def get(self, request):
        # Handle GET request
        obj = Group.objects.filter(status_action=False)
        serializer = GroupSerializer(obj, many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id = request.data.get('id')
            if not id:
                data = {'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Group.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data, status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class GroupListApiView(generics.ListAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent, ]
    queryset = Group.objects.all()
    serializer_class = GroupViewSerializer
    filterset_class = GroupListFilter
    pagination_class = CustomPageNumberPagination

    # def get_queryset(self):
    #     group_curriculum = self.kwargs.get(self.lookup_field[0])
    #     educationLang = self.kwargs.get(self.lookup_field[1])
    #
    #     queryset = Group.objects.filter(group_curriculum_id=group_curriculum)
    #     if educationLang:
    #         queryset = queryset.filter(educationLang_id=educationLang)
    #
    #     return queryset
    #
    # def get(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     if queryset.exists():
    #         serializer = self.get_serializer(queryset, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     else:
    #         response_data = {
    #             "status": False,
    #             "message": "Ushbu o'quv rejaga tegishli guruhlar topilmadi..."
    #         }
    #         return Response(response_data, status=status.HTTP_404_NOT_FOUND)
