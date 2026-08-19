from django.db import models
import uuid
from shared.models import BaseModel
from universty.models import Faculty_type, Faculty


# Create your models here.


class Bspeciality(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    base_spec_id = models.UUIDField()
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=100, )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return "%s" % self.name


class Mspeciality(BaseModel, models.Model):
    base_spec_id = models.UUIDField()
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % self.name


class Ospeciality(BaseModel, models.Model):
    base_spec_id = models.UUIDField()
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % self.name


class Dspeciality(BaseModel, models.Model):
    base_spec_id = models.UUIDField()
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % self.name


class AllSpeciality(BaseModel, models.Model):
    def some_method(self):
        from learning_process.models import Educationtype

    spec_id = models.IntegerField(unique=True, null=True)
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    educationType = models.ForeignKey('learning_process.Educationtype', on_delete=models.CASCADE)
    locality_type = models.ForeignKey(Faculty_type, on_delete=models.CASCADE)
    department = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    bachelorSpecialty = models.ForeignKey(Bspeciality, on_delete=models.SET_NULL, null=True, blank=True)
    masterSpecialty = models.ForeignKey(Mspeciality, on_delete=models.SET_NULL, null=True, blank=True)
    ordinatureSpecialty = models.ForeignKey(Ospeciality, on_delete=models.SET_NULL, null=True, blank=True)
    doctorateSpecialty = models.ForeignKey(Dspeciality, on_delete=models.SET_NULL, null=True, blank=True)
