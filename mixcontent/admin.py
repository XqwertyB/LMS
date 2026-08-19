from django.contrib import admin
from .models import ConnectSpeciality


# Register your models here.

@admin.register(ConnectSpeciality)
class ConnectSpecialityAdmin(admin.ModelAdmin):
    pass
