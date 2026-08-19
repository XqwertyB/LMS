from django.contrib import admin
from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'h_id', 'name', 'group_curriculum', 'educationLang']
    list_filter = ['group_curriculum', 'h_id']

    search_fields = (
        'name',
        'h_id',
    )
