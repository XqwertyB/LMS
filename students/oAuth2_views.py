import logging
import time
from datetime import datetime

import requests
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import AllowOnlyTrustedOrigins
from config.settings import (
    STUDENT_CLIENT_ID, STUDENT_CLIENT_SECRET, STUDENT_REDIRECT_URI,
    STUDENT_AUTHORIZE_URL, STUDENT_TOKEN_URL, STUDENT_RESOURCE_OWNER_URL)
from shared.utils import CustomPageNumberPagination
from user.models import User
from user.serializers import MyTokenObtainPairSerializer
from .client import OAuth2Client
from .models import Student
from .serializers import StudentSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta


class StudentAuthorizationView(APIView):
    """
        OAuth2 tizimi orqali kirish uchun yo‘naltiruvchi URL yaratish
        """

    @swagger_auto_schema(
        tags=["OAuth2 tizimi orqali avtorizatsiya"],
        operation_summary="OAuth2 tizimiga yo‘naltiruvchi havola olish",
        operation_description=(
                "Ushbu endpoint foydalanuvchini tashqi OAuth2 tizimiga avtorizatsiya uchun yo‘naltirish havolasini qaytaradi. "
                "Foydalanuvchi shu havola orqali kirib, ruxsat bergach, tizim `redirect_uri` orqali qaytadi."
        ),
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli javob",
            ),
            400: "Xatolik yuz berdi",
        },
    )
    def get(self, request):
        client = OAuth2Client(
            client_id=STUDENT_CLIENT_ID,
            client_secret=STUDENT_CLIENT_SECRET,
            redirect_uri=STUDENT_REDIRECT_URI,
            authorize_url=STUDENT_AUTHORIZE_URL,
            token_url=STUDENT_TOKEN_URL,
            resource_owner_url=STUDENT_RESOURCE_OWNER_URL
        )

        authorization_url = client.get_authorization_url()

        return Response(
            {
                "message": "Kirish uchun havola muvaffaqiyatli yaratildi.",
                "data": {'authorization_url': authorization_url}
            },
            status=status.HTTP_200_OK
        )


class StudentCallbackView(APIView):
    """
       OAuth2 tizimidan qaytgan javobni qayta ishlash (faqat WEB uchun)
       """

    @swagger_auto_schema(
        tags=["OAuth2 tizimi orqali avtorizatsiya"],
        operation_summary="OAuth2 tizimidan qaytgan javobni qayta ishlash",
        operation_description=(
                "OAuth2 tizimi foydalanuvchi muvaffaqiyatli avtorizatsiyadan o'tgach, "
                "redirect qilinadigan `callback` endpoint. "
                "Bu endpoint `code` query parametri orqali kelgan ruxsat kodini qabul qilib, "
                "backend tokenlarini (access va refresh) yaratadi."
        ),
        manual_parameters=[
            openapi.Parameter(
                name='code',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="OAuth2 serverdan qaytgan avtorizatsiya kodi"
            ),
        ],
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli avtorizatsiya",
            ),
            400: openapi.Response(
                description="Xatolik — `code` yo‘q yoki noto‘g‘ri",
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        full_info: dict[str, any] = {}

        auth_code = request.query_params.get('code')

        if not auth_code:
            return Response(
                {
                    "message": "Tizimga kirish uchun ruxsat kodi topilmadi. Iltimos, qayta urinib ko‘ring.",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        client = OAuth2Client(
            client_id=STUDENT_CLIENT_ID,
            client_secret=STUDENT_CLIENT_SECRET,
            redirect_uri=STUDENT_REDIRECT_URI,
            authorize_url=STUDENT_AUTHORIZE_URL,
            token_url=STUDENT_TOKEN_URL,
            resource_owner_url=STUDENT_RESOURCE_OWNER_URL
        )

        access_token_response = client.get_access_token(auth_code)

        if 'access_token' not in access_token_response:
            return Response(
                {
                    "message": "Kirish uchun ruxsat tokenini olishda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        access_token = access_token_response['access_token']
        user_details = client.get_user_details(access_token)

        if not user_details or 'student_id_number' not in user_details:
            return Response(
                {
                    "message": "Foydalanuvchi ma’lumotlarini olishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=user_details['student_id_number'])

            refresh = RefreshToken.for_user(user)
            refresh.set_exp(lifetime=timedelta(days=1))

            access = AccessToken.for_user(user)
            access.set_exp(lifetime=timedelta(hours=2))

            full_info['backend_token'] = {
                "access": str(access),
                "refresh": str(refresh),
            }

            message = "Tizimga muvaffaqiyatli kirdingiz."

        except ObjectDoesNotExist:
            return Response(
                {
                    "message": (
                        "Tizimda sizning ma'lumotlaringiz topilmadi. "
                        "Iltimos, administrator bilan bog‘laning."
                    ),
                    "data": None
                },
                status=status.HTTP_404_NOT_FOUND
            )

        full_info['details'] = user_details
        full_info['token'] = access_token

        return Response(
            {
                "message": message,
                "data": full_info
            },
            status=status.HTTP_200_OK
        )
