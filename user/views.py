import datetime

from django.core.cache import cache
from django.db.models import Q
from django.db.models import Value
from django.db.models.functions import Concat
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from config.permissions import AllowOnlyTrustedOrigins
from .models import User
from .permission import (
    IsAdmin
)
from .serializers import ChangeSuperUserInformationSerializer  # UserSerializer,
from .serializers import DetailSerializer
from .serializers import LoginRefreshSerializer
from .serializers import LoginSerializer
from .serializers import LogoutSerializer
from .serializers import ResetPasswordSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class TokenRefreshAPIView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogOutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (AllowOnlyTrustedOrigins, IsAuthenticated,)

    @swagger_auto_schema(request_body=LogoutSerializer)
    def post(self, request, *args, **kwargs):
        try:
            # 1️⃣ Refresh tokenni blacklist qilish
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # 2️⃣ Access tokenni Redis deny-listga qo‘shish
            auth_header = request.headers.get("Authorization")

            if auth_header and auth_header.startswith("Bearer "):
                access_str = auth_header.split(" ")[1]
                access_token = AccessToken(access_str)

                jti = access_token["jti"]
                exp = int(access_token["exp"])  # exp — timestamp (int)

                # hozirgi vaqt (timestamp)
                now_ts = int(datetime.datetime.now().timestamp())

                ttl = exp - now_ts
                if ttl < 0:
                    ttl = 0

                cache.set(f"deny:{jti}", True, ttl)

            return Response(
                {"status": True, "message": "Tizimdan chiqildi"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (AllowOnlyTrustedOrigins, IsAuthenticated,)
    serializer_class = ResetPasswordSerializer
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_id = request.user.id
            new_password = serializer.validated_data['password']

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {
                        'message': "Bunday foydalanuvchi mavjud emas."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {'message': "Parol muvaffaqiyatli almashtirildi."},
                status=status.HTTP_200_OK
            )
        return Response(
            {'message': "Xatolik yuz berdi"},
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangeUserInformationAPIView(generics.UpdateAPIView):
    permission_classes = (AllowOnlyTrustedOrigins, IsAdmin,)
    serializer_class = ChangeSuperUserInformationSerializer
    http_method_names = ['patch']

    def get_object(self):
        user_id = self.request.user.id
        user = User.objects.filter(id=user_id)
        return user.first()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(
                {
                    'status': True,
                    "message": "Foydalanuvchi ma'lumotlari muvaffaqiyatli yangilandi.",
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'status': False,
                "message": "Foydalanuvchi ma'lumotlarini yangilashda xatolik yuzaga keldi."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class AdminListAPIView(generics.ListAPIView):
    permission_classes = (AllowOnlyTrustedOrigins, IsAdmin,)
    queryset = User.objects.filter(role='admin')
    serializer_class = DetailSerializer


class AdminDetailAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins, IsAdmin, ]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id)
            serializer = DetailSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data = {
                "message": "Foydalanuvchi topilmadi"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class UsersListAPIView(generics.ListAPIView):
    permission_classes = (AllowOnlyTrustedOrigins, IsAdmin,)
    serializer_class = DetailSerializer

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["created_at"]

    def get_queryset(self):
        queryset = User.objects.all()

        search = self.request.query_params.get("search")

        if search:
            search = search.strip()

            queryset = queryset.annotate(
                full_name=Concat(
                    "first_name",
                    Value(" "),
                    "last_name"
                )
            ).filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return queryset.order_by("created_at")
