from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'department', 'full_name', 'e_status', 'employee_id_number', 'created_at',
                    'updated_at']
    search_fields = ['full_name', 'employee_id_number']
    list_filter = ['e_status', 'department']

    def has_add_permission(self, request):
        return False
