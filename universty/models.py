from django.db import models
import uuid


# Create your models here.

class Otmtype(models.Model):  # OTM turi
    """
        OTM turi malumotlar modeli

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    code = models.CharField(max_length=10, unique=True, null=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Otmshape(models.Model):  # OTM shakli
    """
        OTM shakli malumotlar modeli

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=10, unique=True, null=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=10, unique=True)
    parent = models.CharField(max_length=10)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Otm(models.Model):  # OTM
    """
        OTM haqida malumotlar modeli

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    kod = models.CharField(max_length=250, unique=True)  # 336 Moliya ko`di
    name = models.CharField(max_length=250)  # Nomi
    area_located = models.CharField(max_length=250)  # Hudud
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, related_name='soato')  # Shahar
    phone = models.CharField(max_length=250)  # Kontakt
    stir = models.CharField(max_length=9)
    rektor = models.CharField(max_length=250, null=True, blank=True)
    ownership = models.ForeignKey(Otmtype, related_name='ownership', null=True, on_delete=models.CASCADE)
    universityForm = models.ForeignKey(Otmshape, related_name='universityForm', null=True, on_delete=models.CASCADE)
    address = models.TextField()  # Pochta manzili º
    bank_info = models.TextField()  # Bank ma'lumotlari
    akkreditasiya_info = models.TextField(null=True, blank=True)  # Akkreditasiya ma'lumotlari
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)


class Faculty_type(models.Model):  # Fakultet turi
    """
        Fakultet turi

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=10, unique=True, null=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Faculty(models.Model):  # Fakultet
    """
        Fakultet haqida

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=250)
    hemisid = models.PositiveSmallIntegerField(unique=True, null=True)
    kod = models.CharField(max_length=250, null=True,
                           unique=True)  # Kod OTM kodi olinib chiziqchadan keyin shu yangi ko`di qo`yiladi misol uchun 336-***
    faculty_type = models.ForeignKey(Faculty_type, related_name='faculty_type', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)  # value = faol,faolmas == True , False
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Department(models.Model):  # Kafedra
    """
          Kafedra haqida

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=250)
    hemisid = models.PositiveSmallIntegerField(unique=True, null=True)
    kod = models.CharField(
        max_length=250)  # Kod OTM va Fakultet kodi kodi olinib chiziqchadan keyin shu yangi ko`di qo`yiladi misol uchun 336-101-***
    faculty = models.ForeignKey(Faculty, related_name='faculty', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)  # value = faol,faolmas == True , False
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Section(models.Model):  # Bo`lim
    """
        Bo`lim haqida

    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=250)
    kod = models.CharField(
        max_length=250)  # Kod OTM kodi olinib chiziqchadan keyin shu yangi ko`di qo`yiladi misol uchun 336-***
    status = models.BooleanField(default=True)  # value = faol,faolmas == True , False
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)


class OtmSection(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    code = models.CharField(max_length=10, unique=True, null=True)
    status_action_name = [
        (True, 'Add'),
        (False, 'Delete')
    ]
    status_action = models.BooleanField(choices=status_action_name, default=True, null=True, blank=True)

    def __str__(self):
        return self.name
