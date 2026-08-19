from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import *
from shared.utils import ROLES


class UserManager(BaseUserManager):

    def _create_user(self, username, password, is_staff=False, is_superuser=False, **extra_fields):
        if not username:
            raise ValueError('Login kiritilishi shart...')
        user, created = self.model.objects.get_or_create(
            username=username,
            defaults={
                'is_staff': is_staff,
                'is_active': True,
                'is_superuser': is_superuser,
                'last_login': timezone.now(),
                'date_joined': timezone.now(),
                **extra_fields
            }
        )
        if created:
            user.set_password(password)
            user.role = 'admin'
            user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        return self._create_user(username, password, False, False, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        user = self._create_user(username, password, True, True, **extra_fields)
        return user


class User(AbstractUser, BaseModel, PermissionsMixin):
    role = models.CharField(choices=ROLES, max_length=25)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + self.role + ')'

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
