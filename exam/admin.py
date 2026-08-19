from django.contrib import admin

from .models import (
    Exam,
    Question,
    Answer,
    Result,
    StudentExamAnswer,
    ExamStudent, StudentForTest
)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'comment',
        'curriculum',
        'education_year',
        'semester',
        'exam_type',
        'exam_status',
        'begin_time',
        'end_time',
        'exam_time',
        'max_score',
        'attempts',
        'total_count',
        'is_random',
        'subject',
        'created_at',
        'updated_at'

    ]

    search_fields = ['name', 'curriculum']
    list_filter = ['name', 'semester', 'exam_status', 'exam_type']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'is_active'
    ]


@admin.register(ExamStudent)
class ExamStudentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'exam',
        'student',
        'group',
        'is_active',
        'is_finish',
        'is_login'
    ]

    search_fields = ['student__full_name', 'group__name']
    list_filter = ['exam', 'group', 'is_active', 'is_finish']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'question',
        'isTrue'
    ]


@admin.register(StudentExamAnswer)
class StudentExamAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'question',
        'true_answer',
        'is_selected'
    ]


@admin.register(StudentForTest)
class StudentForTestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'exam',
        'student',
        'json_field'
    ]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'exam',
        'student',
        'group',
        'ip_address',
        'attempts',
        'correct_answer',
        'total_count',
        'max_score',
        'begin_time',
        'end_time',
        'exam_time',
        'percentage',
        'score',
        'time_spent'

    ]

    list_filter = ['exam', ]
