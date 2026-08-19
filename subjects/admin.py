from django.contrib import admin
from .models import Subject, Subjectgroup, Subject_block, \
    Subject_exam_finish, Subject_type, Subject_Curriculum, SubjectDetails, SubjectExamTypes,RatingGrade


# Register your models here.

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'hemis_id', 'code', 'name']
    search_fields = ['name','hemis_id']


@admin.register(Subjectgroup)
class SubjectgroupAdmin(admin.ModelAdmin):
    pass

@admin.register(RatingGrade)
class RatingGradeAdmin(admin.ModelAdmin):
    pass

@admin.register(Subject_block)
class Subject_blockAdmin(admin.ModelAdmin):
    pass


@admin.register(Subject_exam_finish)
class Subject_exam_finishAdmin(admin.ModelAdmin):
    pass


@admin.register(Subject_type)
class Subject_typeAdmin(admin.ModelAdmin):
    pass


class DetailsInline(admin.StackedInline):  # You can also use TabularInline for a more compact display
    model = SubjectDetails
    extra = 4


class SubjectExamTypesInline(admin.StackedInline):  # You can also use TabularInline for a more compact display
    model = SubjectExamTypes
    extra = 4


@admin.register(Subject_Curriculum)
class Subject_CurriculumAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'subject_curriculum', 'subject_semestr','ratingGrade']
    list_filter = ['id','subject_curriculum', 'subject_semestr', 'subject_departmant']
    inlines = [DetailsInline, SubjectExamTypesInline]
