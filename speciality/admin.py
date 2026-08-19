from django.contrib import admin
from .models import Bspeciality, Mspeciality, Ospeciality, Dspeciality, AllSpeciality


# Register your models here.


@admin.register(Bspeciality)
class BspecialityAdmin(admin.ModelAdmin):
    list_display = ['base_spec_id', 'name', 'code', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['base_spec_id']
    ordering = ['-created_at',]


@admin.register(Mspeciality)
class MspecialityAdmin(admin.ModelAdmin):
    list_display = ['base_spec_id', 'name', 'code', 'created_at','updated_at']
    search_fields = ['name', 'code']
    list_filter = ['base_spec_id']
    ordering = ['-created_at', ]


@admin.register(Ospeciality)
class OspecialityAdmin(admin.ModelAdmin):
    list_display = ['base_spec_id', 'name', 'code', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['base_spec_id']
    ordering = ['-created_at', ]


@admin.register(Dspeciality)
class DspecialityAdmin(admin.ModelAdmin):
    list_display = ['base_spec_id', 'name', 'code', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['base_spec_id']
    ordering = ['-created_at', ]


@admin.register(AllSpeciality)
class AllSpecialityAdmin(admin.ModelAdmin):
    list_display = ['id','spec_id','name','code']
    list_filter = ['spec_id','bachelorSpecialty__id']
    pass
