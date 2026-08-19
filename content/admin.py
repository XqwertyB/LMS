from django.contrib import admin
from .models import Content, Roletype, Content_teacher, Topic, Video_content, File_content, Task, Task_type, Task_file, \
    Task_students, Student_file, LessonRoom
from import_export import resources
from import_export.admin import ExportMixin
from django.db.models import Count, Q
# Register your models here.
from admin_totals.admin import ModelAdminTotals

from django.contrib.admin import RelatedOnlyFieldListFilter

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['subject_id', 'semestr_action']
    list_filter = ['curriculum_id', 'content_semestrs', 'semestr_action']


@admin.register(Roletype)
class RoletypeAdmin(admin.ModelAdmin):
    pass


# Update the admin class
from django.db.models import Count, Q

from django.db.models import Count


@admin.register(Content_teacher)
class Content_teacherAdmin(ExportMixin, ModelAdminTotals, admin.ModelAdmin):
    list_display = (
        'teacher_id',
        'get_department',
        'content_id',
        'get_content_semester',
        'video_count_display',
        'file_count_display',
        'task_count',
        'get_bachelor_specialty',
        'get_education_form',
        'get_education_year',
        'get_curriculum_department',
    )

    list_filter = (
        'content_id__level',
        'video_count',
        'content_id__semestr_action',
        ('content_id__curriculum_id__new_specialty__bachelorSpecialty',
         RelatedOnlyFieldListFilter),
        ('content_id__curriculum_id__educationform',
         RelatedOnlyFieldListFilter),
        ('content_id__curriculum_id__educationyear',
         RelatedOnlyFieldListFilter),
        ('content_id__content_semestrs',
         RelatedOnlyFieldListFilter),  # 👈 filter ishlaydi
        ('content_id__curriculum_id__department',
         RelatedOnlyFieldListFilter),
    )

    def get_department(self, obj):
        if obj.teacher_id and obj.teacher_id.department:
            return obj.teacher_id.department
        return "-"

    def level(self, obj):
        return obj.content_id.level

    level.short_description = 'Level'

    def get_bachelor_specialty(self, obj):
        if obj.content_id and obj.content_id.curriculum_id \
                and obj.content_id.curriculum_id.new_specialty:
            return obj.content_id.curriculum_id.new_specialty.bachelorSpecialty
        return "-"

    get_bachelor_specialty.short_description = "Bachelor Specialty"

    def get_education_form(self, obj):
        try:
            return obj.content_id.curriculum_id.educationform
        except AttributeError:
            return "-"

    get_education_form.short_description = "Education Form"

    def get_education_year(self, obj):
        try:
            return obj.content_id.curriculum_id.educationyear
        except AttributeError:
            return "-"

    get_education_year.short_description = "Education Year"

    def get_content_semester(self, obj):
        try:
            return obj.content_id.content_semestrs
        except AttributeError:
            return "-"

    get_content_semester.short_description = "Semester"

    def get_curriculum_department(self, obj):
        try:
            return obj.content_id.curriculum_id.department
        except AttributeError:
            return "-"

    get_curriculum_department.short_description = "Department"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Annotatsiya qilish
        queryset = queryset.annotate(
            video_count_total=Count('content_teacher_connect__topic_videos', distinct=True),
            file_count_total=Count('content_teacher_connect__topic_files', distinct=True),
        )

        # Butun queryset bo‘yicha umumiy video va fayllarni hisoblash
        totals = queryset.aggregate(
            total_videos=Count('content_teacher_connect__topic_videos', distinct=True),
            total_files=Count('content_teacher_connect__topic_files', distinct=True)
        )

        self.total_video_count = totals['total_videos'] or 0
        self.total_file_count = totals['total_files'] or 0

        return queryset

    def video_count_display(self, obj):
        return obj.video_count_total

    video_count_display.short_description = 'Video Count'

    def file_count_display(self, obj):
        return obj.file_count_total

    file_count_display.short_description = 'File Count'

    def changelist_view(self, request, extra_context=None):
        """
        Admin sahifasida umumiy video va fayl sonlarini chiqarish.
        """
        if extra_context is None:
            extra_context = {}

        # Qo'shimcha kontekstga umumiy sonlarni qo‘shish
        extra_context['total_video_count'] = getattr(self, 'total_video_count', 0)
        extra_context['total_file_count'] = getattr(self, 'total_file_count', 0)

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['id', 'teacher_id', 'number', 'name', 'get_group_lang_name', 'created_at', 'content_id_topic', ]
    list_filter = ['teacher_id', 'content_id_topic', ]

    def get_group_lang_name(self, obj):
        return obj.content_teacher_connect.group_lang.name if obj.content_teacher_connect else None

    get_group_lang_name.short_description = 'Group Language'


@admin.register(Video_content)
class Video_contentAdmin(admin.ModelAdmin):
    pass


@admin.register(File_content)
class File_contentAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    pass


@admin.register(Task_type)
class Task_typeAdmin(admin.ModelAdmin):
    pass


@admin.register(Task_file)
class Task_fileAdmin(admin.ModelAdmin):
    pass


@admin.register(Task_students)
class Task_studentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_group_id', 'tasks_id', 'task_student_id', 'is_status', 'is_passed']
    list_filter = ['task_group_id', 'tasks_id', 'task_student_id']
    pass


@admin.register(Student_file)
class Student_fileAdmin(admin.ModelAdmin):
    pass


@admin.register(LessonRoom)
class LessonRoomAdmin(admin.ModelAdmin):
    pass
