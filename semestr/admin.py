from django.contrib import admin
from .models import HCourse, Hsemester, Hsemester_action, CurriculumWeeks


# Register your models here.

@admin.register(HCourse)
class HCourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Hsemester)
class HsemesterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']


@admin.register(Hsemester_action)
class Hsemester_actionAdmin(admin.ModelAdmin):
    list_display = ['id', 'h_id', 'semester', 'current', 'education_year', 'curriculum', 'get_educationform']
    list_filter = ['semester', 'current', 'curriculum', 'education_year', 'curriculum__educationform']

    def get_educationform(self, obj):
        return obj.curriculum.educationform.name  # Or another field you want to display

    get_educationform.short_description = 'Education Form'

    pass


@admin.register(CurriculumWeeks)
class CurriculumWeeksAdmin(admin.ModelAdmin):
    list_display = ['h_id', 'current', ]
    pass
