"""
Bu view ichida foydalanuvchi harakatlarini kuzatish va ko'rsatish uchun kerakli kod yoziladi.

 - API endpointlari yaratish,
 - Foydalanuvchi harakatlarini filtrlash va qidirish funksiyalarini qo'shish,
 - Harakatlar jurnalini eksport qilish imkoniyatlarini taqdim etish,
 - Va boshqa tegishli funksiyalarni amalga oshirish.

"""
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from action_logs.models import APILogsModel
from action_logs.serializers import APILogsSerializer
from config.permissions import AllowOnlyTrustedOrigins
from shared.utils import CustomPageNumberPagination
from user.permission import IsAdmin


class APILogsListAPIView(generics.ListAPIView):
    """
    📜 API loglar ro‘yxati (admin uchun)
    """
    serializer_class = APILogsSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin]

    @swagger_auto_schema(
        operation_description="API loglarni olish (user bo‘yicha filter mavjud)",
        tags=['API Logs'],
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="User ID bo‘yicha filter",
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = APILogsModel.objects.all().select_related('user').order_by('-added_on')

        user_id = self.request.query_params.get('user_id')

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset
