from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.validation_error import CustomValidationError
from user.models import User
from django.core.cache import cache

MAX_FAILED_ATTEMPTS = 5         # username + IP limit
USER_BLOCK_TIME = 600           # 10 minutes

MAX_IP_ATTEMPTS = 20            # IP global limit
IP_BLOCK_TIME = 3600            # 1 hour

def get_client_ip(request):
    """Real foydalanuvchining IP manzilini olish"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return {
            "access": str(token.access_token),
            "refresh": str(token)
        }


class LoginSerializer(MyTokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.current_user = None
        self.fields['username'] = serializers.CharField(required=False)  # optional username

    def auth_validate(self, data):
        request = self.context['request']
        username = data.get('username')
        password = data.get('password')
        ip = get_client_ip(request)

        # -----------------------------------------
        # 1) IP umumiy limitini tekshiramiz
        # -----------------------------------------
        ip_key = f"ip_attempts_{ip}"
        ip_attempts = cache.get(ip_key, 0)

        if ip_attempts >= MAX_IP_ATTEMPTS:
            raise CustomValidationError({
                'success': False,
                'message': "Bu IP juda ko‘p marta urindi. 1 soatdan keyin urinib ko‘ring."
            })

        # -----------------------------------------
        # 2) Username bo'lsa → username+IP limit ishlaydi
        # Username bo‘lmasa → username limit qo‘llanmaydi
        # -----------------------------------------
        if username:
            username_exists = True
            user_ip_key = f"login_attempts_{ip}_{username}"
            attempts = cache.get(user_ip_key, 0)

            if attempts >= MAX_FAILED_ATTEMPTS:
                raise CustomValidationError({
                    'success': False,
                    'message': "Ko‘p xato urinishlar! 10 daqiqadan keyin urinib ko‘ring."
                })
        else:
            username_exists = False
            user_ip_key = None
            attempts = None

        # -----------------------------------------
        # 3) Parolni tekshiramiz
        # -----------------------------------------
        if not password:
            raise CustomValidationError({
                'success': False,
                'message': "Parol kiriting!"
            })

        # -----------------------------------------
        # 4) Authentication
        # -----------------------------------------
        current_user = authenticate(username=username, password=password)

        if current_user is None:
            # Username bo‘lsa → username limitni oshiramiz
            if username_exists:
                attempts = (attempts or 0) + 1
                cache.set(user_ip_key, attempts, USER_BLOCK_TIME)

            # IP global limitni oshiramiz
            ip_attempts += 1
            cache.set(ip_key, ip_attempts, IP_BLOCK_TIME)

            raise CustomValidationError({
                'success': False,
                'message': (
                    "Noto‘g‘ri login yoki parol!\n"
                    f"Urinishlar: {attempts if attempts else 0}/{MAX_FAILED_ATTEMPTS}\n"
                    f"IP urinishlari: {ip_attempts}/{MAX_IP_ATTEMPTS}"
                )
            })

        # -----------------------------------------
        # 5) To‘g‘ri login → barcha limitlarni reset qilamiz
        # -----------------------------------------
        if username_exists:
            cache.delete(user_ip_key)
        cache.delete(ip_key)

        self.current_user = current_user

    def validate(self, data):
        self.auth_validate(data)
        return self.get_token(self.current_user)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ChangeSuperUserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'role']


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, required=True)
    confirm_password = serializers.CharField(min_length=8, required=True)

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise CustomValidationError(
                {
                    'status': False,
                    'message': "Parollar mos kelmaydi."
                }
            )

        return data


class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        try:
            access_token_instance = AccessToken(data['access'])
            user_id = access_token_instance['user_id']
            user = User.objects.get(id=user_id)
            update_last_login(None, user)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("User not found.")
        return data
