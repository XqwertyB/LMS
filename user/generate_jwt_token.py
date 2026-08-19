from datetime import timedelta, datetime
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistMixin
from config import settings
import uuid


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):
        expiration_times = {
            'student': timedelta(minutes=45),
            'admin': timedelta(minutes=52),
        }

        expiration_time = expiration_times.get(user.role.lower(), timedelta(minutes=30))
        exp = datetime.utcnow() + expiration_time
        header = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            'exp': exp,
            'role': user.role,
            'user_id': str(user.id),
            'jti': str(uuid.uuid4()),
            "token_type": "refresh",
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY, headers=header)

        return RefreshToken(token)


# def generate_jwt_token(user):
#     expiration_times = {
#         'student': timedelta(minutes=45),
#         'admin': timedelta(minutes=52),
#     }
#
#     expiration_time = expiration_times.get(user.role.lower(), timedelta(minutes=15))
#     exp = datetime.utcnow() + expiration_time
#
#     header = {
#         "alg": "HS256",
#         "typ": "JWT"
#     }
#     payload = {
#         'exp': exp,
#         'role': user.role,
#         'user_id': str(user.id),
#         'jti': str(uuid.uuid4()),
#         "token_type": "refresh",
#     }
#
#     token = jwt.encode(payload=payload, key=settings.SECRET_KEY, headers=header)
#
#     return RefreshToken(token)
