from django.contrib import admin

from autoproctor.models import ScreenModel


@admin.register(ScreenModel)
class ScreenModelAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'student',
        'exam',
        'attempts',
        'is_active',
    ]
