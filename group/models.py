from django.db import models
from shared.models import BaseModel
from universty.models import Faculty
from speciality.models import Bspeciality,AllSpeciality
from learning_process.models import Curriculum, Educationlang


class Group(BaseModel, models.Model):
    """
    - Group modeli
    from learning_process.models import Curriculum
    cur = Curriculum.objects.all()
    from group.models import Group
    obj = Group.objects.all()

    """
    h_id = models.PositiveIntegerField(unique=True, null=True)
    name = models.CharField(max_length=200)
    group_curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='group_curriculum',
                                         null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='g_faculty', null=True)
    specialty = models.ForeignKey(Bspeciality, on_delete=models.SET_NULL,null=True, related_name='g_specialty')
    new_specialty = models.ForeignKey(AllSpeciality, on_delete=models.SET_NULL,null=True, related_name='g_specialty')
    educationLang = models.ForeignKey(Educationlang, on_delete=models.CASCADE, related_name='g_educationlang')

    def __str__(self):
        return self.name
