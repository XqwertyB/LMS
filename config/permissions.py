from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .settings import ALLOWED_ORIGINS
# ALLOWED_ORIGINS = [
#     "https://test-admin.tsue.uz",
#     "https://api-lms-test.tsue.uz",
#     "https://test-teacher.tsue.uz",
#     "https://test-lms.tsue.uz",
#     "https://admin.tsue.uz",
#     "https://api-lms.tsue.uz",
#     "https://teacher.tsue.uz",
#     "https://lms.tsue.uz",
#
# ]

class AllowOnlyTrustedOrigins(BasePermission):

    def has_permission(self, request, view):
        origin = request.headers.get("Origin")

        # 1️⃣ Agar Origin yo‘q → Postman, curl, mobile ilova:
        #    Origin faqat browserdan keladi, shuning uchun bunday requestlarga ruxsat beramiz
        if origin is None:
            return True

        # 2️⃣ Origin bor, lekin ro‘yxatda yo‘q → browserdan kelgan hujum
        if origin not in ALLOWED_ORIGINS:
            raise PermissionDenied("Forbidden origin: {}".format(origin))

        # 3️⃣ Origin ruxsat etilgan
        return True

from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class RedisJWTAuthentication(JWTAuthentication):

    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)

        jti = token.get("jti")

        # Redis deny-listni tekshirish
        if cache.get(f"deny:{jti}") is not None:
            raise AuthenticationFailed("Access token revoked")

        return token