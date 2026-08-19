from django.contrib import admin

from .models import Otmtype,Otmshape,Otm,Faculty,Faculty_type,Department,Section,City,OtmSection


@admin.register(Otm)
class OtmAdmin(admin.ModelAdmin):
    pass

@admin.register(Otmtype)
class OtmtypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Otmshape)
class OtmshapeAdmin(admin.ModelAdmin):
    pass

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_filter = ['hemisid']
    list_display = ['name','hemisid','kod']
    pass

@admin.register(Faculty_type)
class Faculty_typeAdmin(admin.ModelAdmin):
    pass

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'hemisid']
    list_filter = ['status']
    pass


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass

@admin.register(OtmSection)
class OtmSectionAdmin(admin.ModelAdmin):
    pass