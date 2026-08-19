from rest_framework.views import APIView
from rest_framework.response import Response

from config.permissions import AllowOnlyTrustedOrigins
from group.models import Group
import datetime
from learning_process.models import Curriculum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from django.db.models import Count, Q
from group.serializers import GroupViewSerializer
from django.db import transaction

from shared.permissions import IsAdminOrTeacher
from shared.utils import CustomPageNumberPagination
from content.models import Content_teacher
from .models import Middle_exam
from .seializers import Middle_exam_list_Serializer


class ALL_GET_MIDDLE_EXAM(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrTeacher, ]
    def get(self, request, connect_id):
        # print(request.user.employee)
        try:
            connect = Content_teacher.objects.get(id=connect_id, teacher_id=request.user.employee)
        except Content_teacher.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': 'Oraliq topilmadi...'
                }, status=status.HTTP_404_NOT_FOUND
            )
        try:
            middle_exam = Middle_exam.objects.filter(status_action=True, connect=connect)
            seralizer = Middle_exam_list_Serializer(middle_exam, many=True)
        except Exception as ex:
            return Response(
                {
                    'status': False,
                    'message': 'Oraliq muamo bor...',
                    'system_errors': str(ex)
                }, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {'message': True, 'results': seralizer.data}, status.HTTP_200_OK
        )
