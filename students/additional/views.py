from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from students.models import Student
from students.serializers import StudentSerializer, StudentIsActiveUpdateSerializer


class FullStudentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Student.objects.all().order_by('student_id_number')
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['group', 'faculty', 'educationLang', 'paymentForm', 'educationYear', 'educationType',
                        'educationForm', 'studentStatus', 'specialty', 'level', 'semester', 'socialCategory']
    search_fields = ['full_name', 'student_id_number']


class StudentBulkUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    """
    Barcha studentlarning is_active qiymatini yangilash
    """
    queryset = Student.objects.all()
    serializer_class = StudentIsActiveUpdateSerializer
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        is_active = request.data.get("is_active")

        if isinstance(is_active, bool):
            pass
        elif isinstance(is_active, str) and is_active.lower() in ["true", "false"]:
            is_active = is_active.lower() == "true"
        else:
            return Response(
                {"error": "Faqat true/false (boolean yoki string) qiymati yuborilishi kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = Student.objects.update(is_active=is_active)

        if is_active:
            message = f"{updated_count} ta student statusi Faol statusga yangilandi."
        else:
            message = f"{updated_count} ta student statusi Nofaol statusga yangilandi."

        return Response(
            {
                "message": message
            },
            status=status.HTTP_200_OK
        )
