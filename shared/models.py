import uuid

from django.db import models


class BaseModel(models.Model):
    """
    - Bu model har doim id, created_at va updated_at fieldlarni qayta yozmasdan har qanday modelda inherit qilib ishlash imkonini beruvchi class.

    - Bu class modelda yaratilmaydi sababi abstract=True deyilgani uchun.

    - Demak, qayta qayta yuqoridagi filedlarni yozmaslik uchun ishlab chiqilgan model

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    class Meta:
        abstract = True


class EduType(BaseModel, models.Model):
    """
    - Mutaxasislik turi modeli

    - Masalan [Mahalliy, Qo'shma, Bo'lim, ...]

    """
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=2)

    def __str__(self):
        return self.name


class EducationType(BaseModel, models.Model):
    """
    - Ta'lim turi modeli

    - Masalan [Bakalavr, Magistr, Ordinatura, ...]

    """
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=2,unique=True)

    def __str__(self):
        return self.name


class H_Student_Status(BaseModel, models.Model):
    """
    - Talaba statusi turlari modeli

    - Masalan [Chetlashgan, Bitirgan, O‘qimoqda, ...]

    """
    name = models.CharField(max_length=35)
    code = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class EnterOTMYear(BaseModel, models.Model):
    """
    - O'qishga kirgan yili modeli

    - Masalan [2022, 2023, 2024, ...]

    """
    name = models.CharField(max_length=12)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


class FormOfPayment(BaseModel, models.Model):
    """
    - Ta'lim shakli modeli

    - Masalan [Davlat granti, Kontrakt]

    """
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


class H_Social_Category(BaseModel, models.Model):
    """
    "name": "Talabalarning ijtimoiy toifalari",
    "options": [
        {
            "code": "10",
            "name": "Boshqa"
        },
        {
            "code": "11",
            "name": "To‘liq davlat ta’minotida bo‘lgan yetim bolalar"
        },
        {
            "code": "12",
            "name": "1 va 2-guruh nogironligi bo‘lgan talabalar"
        },
        {
            "code": "13",
            "name": "Ota-ona qaramog‘idan mahrum bo‘lgan bolalar"
        },
        {
            "code": "14",
            "name": "Halok bo‘lgan xarbiylar farzandlari"
        }
    ]

    """
    name = models.CharField(max_length=130)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


class H_Accommodation(BaseModel, models.Model):
    """
    "name": "Talabalar yashash joylari turlari",
    "options": [
        {
            "code": "11",
            "name": "O‘z uyida"
        },
        {
            "code": "12",
            "name": "Qarindoshining uyida"
        },
        {
            "code": "13",
            "name": "Tanishining uyida"
        },
        {
            "code": "14",
            "name": "Ijaradagi uyda"
        },
        {
            "code": "15",
            "name": "Talabalar turar joyida"
        }
    ]
    """
    name = models.CharField(max_length=130)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


class H_Citizenship_type(BaseModel, models.Model):
    """
        "name": "Fuqarolik holatlari turlari",
        "options": [
          {
            "code": "11",
            "name": "O‘zbekiston Respublikasi fuqarosi"
          },
          {
            "code": "12",
            "name": "Xorijiy davlat fuqarosi"
          },
          {
            "code": "13",
            "name": "Fuqaroligi yo‘q shaxslar"
          }
        ]
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


class Gender(BaseModel, models.Model):
    """
    Jins modeli

    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class Roles(BaseModel, models.Model):
    """
    Rollar modeli

    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Citizenship(BaseModel, models.Model):
    """
    Fuqarolik modeli

    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Nation(BaseModel, models.Model):
    """
    Millat modeli

    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class State(BaseModel, models.Model):
    """
    Davlatlar nomlari modeli

    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class Province(BaseModel, models.Model):
    """
    Viloyatlar modeli

    """
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='state')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class District(BaseModel, models.Model):
    """
    Tumanlar modeli

    """
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='province')
    name = models.CharField(max_length=100)
    h_id = models.IntegerField(null=True, unique=True)
    code = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return self.name


class AcademicDegree(BaseModel, models.Model):
    """
    Ilmiy daraja nomlari modeli

    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Scientific(BaseModel, models.Model):
    """
    Ilmiy unvon nomlari modeli

    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Year(BaseModel, models.Model):
    """
    Yillar nomi modeli

    """
    name = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class EmployeeStatus(BaseModel, models.Model):
    """
    - Status nomi modeli

    - Masalan [Ishlamoqda, Ta'tilda, Bo'shagan]

    """
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class ExamTypes(BaseModel, models.Model):
    """
    - Nazorat turi modeli

    - Masalan [Joriy, Oraliq, Yakuniy, ...]

    """
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=2)

    def __str__(self):
        return self.name


class TrainingType(BaseModel, models.Model):
    """
    - O'quv mashg'ulotlari turlari
    - Masalan [ Ma’ruza,Amaliy,Laboratoriya,Mustaqil ta‘lim, ...]
    """
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=2)

    def __str__(self):
        return self.name
