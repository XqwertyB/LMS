from django.db import models
from shared.models import BaseModel
from universty.models import Faculty_type, Faculty
from speciality.models import Bspeciality, Mspeciality, Ospeciality
from learning_process.models import Educationtype, Science_branch


# Create your models here.
class ConnectSpeciality(BaseModel, models.Model):
    conspec_id = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=250, null=True)
    localitytype = models.ForeignKey(Faculty_type, on_delete=models.CASCADE, related_name='con_localitytype')
    educationtype = models.ForeignKey(Educationtype, on_delete=models.CASCADE,
                                      related_name='con_educationtype')
    department = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name="con_department")
    bachelorSpecialty = models.ForeignKey(Bspeciality, on_delete=models.SET_NULL, null=True,
                                          related_name="con_bachelor")
    masterSpecialty = models.ForeignKey(Mspeciality, on_delete=models.SET_NULL, null=True,
                                        related_name="con_master")
    doctorateSpecialty = models.ForeignKey(Science_branch, on_delete=models.SET_NULL, null=True,
                                           related_name="con_doctorate")
    ordinatureSpecialty = models.ForeignKey(Ospeciality, on_delete=models.SET_NULL, null=True,
                                            related_name="con_ordinature")

    def __str__(self):
        return f"{self.name}"
