import urllib
from io import BytesIO

from django.db.models import Max
from django.http import StreamingHttpResponse
from drf_yasg.utils import swagger_auto_schema
import zipfile
import os

from config.permissions import AllowOnlyTrustedOrigins
from config.settings import BASE_DIR
from shared.permissions import IsStudent, IsAdminOrStudent
from students.models import Student
from .filters import ScreenModelFilter
from .serializers import ScreenModelSerializer, ScreenListSerializer, ScreenDetailSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import ScreenModel


class ScreenModelAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsStudent]
    @swagger_auto_schema(request_body=ScreenModelSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ScreenModelSerializer(data=request.data)
        if serializer.is_valid():
            student_id = serializer.validated_data['student'].id
            exam_id = serializer.validated_data['exam'].id
            attempts_count = ScreenModel.objects.filter(student_id=student_id, exam_id=exam_id).count()
            remaining_attempts = 10 - attempts_count

            if attempts_count >= 10:
                try:
                    ScreenModel.objects.filter(student_id=student_id, exam_id=exam_id).update(is_active=False)
                except Exception:
                    pass
                return Response(
                    {
                        'is_active': False,
                        'message': 'Imtihondan chetlashtirildingiz...'
                    }, status=status.HTTP_200_OK)
            else:
                message = None
                if remaining_attempts == 3:
                    message = 'Sizning 3 ta imkoniyatingiz qoldi. Keyin imtihondan chetlashtirilasiz...'

                elif remaining_attempts == 2:
                    message = 'Sizning 2 ta imkoniyatingiz qoldi. Keyin imtihondan chetlashtirilasiz...'

                elif remaining_attempts == 1:
                    message = 'Sizning 1 ta imkoniyatingiz qoldi. Keyin imtihondan chetlashtirilasiz...'

                if serializer.is_valid(raise_exception=True):
                    result = serializer.save()
                    result.attempts = attempts_count + 1
                    result.save()
                    if message is not None:
                        return Response(
                            {
                                'message': message
                            }, status=status.HTTP_201_CREATED)
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScreenListsAPIView(generics.ListAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent]
    serializer_class = ScreenListSerializer
    filterset_class = ScreenModelFilter

    def get_queryset(self):
        queryset = ScreenModel.objects.all()
        latest_created_at_ids = queryset.values('student_id', 'exam_id').annotate(
            max_created_at=Max('created_at')).values_list('max_created_at', flat=True)
        latest_objects = ScreenModel.objects.filter(created_at__in=latest_created_at_ids)
        return latest_objects


class ScreenDetailView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminOrStudent]
    def get(self, request, student_id, exam_id):
        queryset = ScreenModel.objects.filter(student_id=student_id, exam_id=exam_id)
        if queryset.exists():
            student = Student.objects.get(id=student_id)
            serializer = ScreenDetailSerializer(queryset, many=True)

            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for image_file in serializer.data:
                    file_name = image_file.get('image')
                    image_name = os.path.basename(file_name)
                    decoded_url = urllib.parse.unquote(str(BASE_DIR) + file_name)

                    with open(decoded_url, "rb") as f:
                        zipf.writestr(image_name, f.read())

            zip_buffer.seek(0)
            response = StreamingHttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={student.student_id_number}.zip'
            return response
        else:
            return Response(
                {
                    'status': False,
                    'message': "Ma'lumot topilmadi..."
                }, status=status.HTTP_400_BAD_REQUEST)
