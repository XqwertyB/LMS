from django.db import models
import uuid


# Create your models here.
class HemisModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    fio = models.CharField(max_length=250, null=True, blank=True, unique=True)
    hemis_login = models.CharField(max_length=250, null=True, blank=True)
    hemis_password = models.CharField(max_length=250, null=True, blank=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fio


class HemisToken(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hemis_user = models.ForeignKey(HemisModel, on_delete=models.CASCADE, related_name='hemis_tokens')
    hemis_token = models.CharField(max_length=250)
    hemis_token_type = models.CharField(max_length=250)
    hemis_begin = models.DateTimeField(null=True, blank=True)
    hemis_end = models.DateTimeField(null=True, blank=True)
    status_name = [
        (True, 'Active'),
        (False, 'Deactive')
    ]
    status = models.BooleanField(choices=status_name, default=True)


class Hemis_Base(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hemis_user = models.ForeignKey(HemisModel, on_delete=models.CASCADE, related_name='hemis_base')
    base_url = models.CharField(max_length=250, null=True, blank=True)
    path_url = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    comment = models.TextField()
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)
    own_uniq = models.PositiveSmallIntegerField(null=True, unique=True)
    openapi_name = [
        (True, 'Ochiq api',),
        (False, 'Yopiq api')
    ]
    openapi = models.BooleanField(choices=openapi_name, default=True)

    def __str__(self):
        return self.name


class Hemis_sub(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=250)
    uniqcode = models.PositiveSmallIntegerField(null=True, unique=True, blank=True)
    own_uniq = models.PositiveSmallIntegerField(null=True, unique=True, blank=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

