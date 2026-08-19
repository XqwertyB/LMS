from django.contrib import admin
from .models import Educationyear, Educationtype, Educationform, MarkingSystem, Curriculum, Science_branch, \
    Educationlang


# Register your models here.


@admin.register(Educationyear)
class EducationyearAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'current']


@admin.register(Educationtype)
class EducationtypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name']


@admin.register(Educationform)
class EducationformAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name']


@admin.register(MarkingSystem)
class MarkingSystemAdmin(admin.ModelAdmin):
    pass


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','cur_id','educationform','educationyear']
    list_filter = ['educationform','name','cur_id','educationyear']
    pass


@admin.register(Science_branch)
class Science_branchAdmin(admin.ModelAdmin):
    pass


@admin.register(Educationlang)
class EducationlangAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name']
