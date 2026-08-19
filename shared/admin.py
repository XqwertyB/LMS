from django.contrib import admin

from .models import (
    Gender,
    H_Student_Status,
    FormOfPayment,
    State,
    H_Citizenship_type,
    H_Social_Category,
    H_Accommodation,
    EmployeeStatus,
    ExamTypes,
    TrainingType
)


@admin.register(ExamTypes)
class ExamTypesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'created_at', 'updated_at']
    list_display_links = None
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(TrainingType)
class TrainingTypesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(H_Student_Status)
class H_Student_Status_Admin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(FormOfPayment)
class FormOfPayment_Admin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(State)
class State_Admin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(H_Citizenship_type)
class H_Citizenship_type_Admin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(H_Social_Category)
class H_Social_Category_Admin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(H_Accommodation)
class H_Accommodation_Admin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(EmployeeStatus)
class EmployeeStatus_Admin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'updated_at']
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
