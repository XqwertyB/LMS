from django.db import models

from shared.models import BaseModel, EmployeeStatus, Gender
from universty.models import Department
from user.models import User


class Employee(BaseModel):
    """
        Xodimlar bazasi modeli, ushbu modelda avtomatik va
        ruchnoy holatda to'ldirish imkoniyati yaratilishi shart
    """
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='employee', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='e_department')
    e_status = models.ForeignKey(EmployeeStatus, on_delete=models.CASCADE, related_name='e_status')
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, related_name='e_gender')
    employee_id_number = models.CharField(max_length=40, unique=True, db_index=True)
    role = models.CharField(max_length=25, default='employee', editable=False)
    first_name = models.CharField(max_length=70)
    second_name = models.CharField(max_length=70)
    full_name = models.CharField(max_length=170)
    father_name = models.CharField(max_length=70)
    birth_date = models.CharField(max_length=25)

    def __str__(self):
        return self.full_name
