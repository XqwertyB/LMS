from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_id_number', 'image', 'full_name', 'created_at', 'updated_at']
    search_fields = ['full_name', 'student_id_number']
    list_filter = ['group']
    search_help_text = 'FIO'
