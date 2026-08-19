# retraining/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db import models
from .models import (
    ReTrainingGroup, ReTrainingStudent, Assignment,
    TestQuestion, TestQuestionOption, AssignmentSubmission, TestAnswer
)


# ============================================================================
# INLINE CLASSES
# ============================================================================

class ReTrainingStudentInline(admin.TabularInline):
    model = ReTrainingStudent
    extra = 0
    readonly_fields = ['enrolled_at', 'days_in_course']
    fields = [
        'student', 'enrolled_at', 'days_in_course'
    ]

    def days_in_course(self, obj):
        if obj.enrolled_at:
            delta = timezone.now() - obj.enrolled_at
            return f"{delta.days} дней"
        return "-"

    days_in_course.short_description = 'В курсе'


class TestQuestionOptionInline(admin.TabularInline):
    model = TestQuestionOption
    extra = 2
    fields = ['option_text', 'is_correct', 'order']
    ordering = ['order']


class TestQuestionInline(admin.StackedInline):
    model = TestQuestion
    extra = 0
    fields = [
        'question_text', 'question_type', 'points', 'order',
        'is_required', 'is_active', 'correct_answer'
    ]
    ordering = ['order']

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and obj.assignment_type != 'test':
            return 0
        return super().get_max_num(request, obj, **kwargs)


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    readonly_fields = ['submissions_count', 'assignment_is_active']
    fields = [
        'title', 'assignment_type', 'status', 'start_datetime',
        'end_datetime', 'max_attempts', 'submissions_count'
    ]

    def submissions_count(self, obj):
        if obj.pk:
            return obj.submissions.count()
        return 0

    submissions_count.short_description = 'Сдач'

    def assignment_is_active(self, obj):
        if obj.pk:
            return obj.is_active
        return False

    assignment_is_active.short_description = 'Активно'
    assignment_is_active.boolean = True


class TestAnswerInline(admin.TabularInline):
    model = TestAnswer
    extra = 0
    readonly_fields = ['question', 'is_correct', 'points_earned']
    fields = ['question', 'selected_options', 'text_answer', 'is_correct', 'points_earned']

    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# MAIN ADMIN CLASSES
# ============================================================================

@admin.register(ReTrainingGroup)
class ReTrainingGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'teacher', 'language',
        'students_count_display', 'max_students', 'created_at'
    ]
    list_filter = [
        'language',  'teacher', 'created_at'
    ]
    search_fields = ['name', 'description', 'teacher__first_name', 'teacher__last_name']
    readonly_fields = [
        'students_count_display', 'created_at'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'max_students')
        }),
        ('Параметры обучения', {
            'fields': ('teacher', 'language', 'faculty', 'speciality')
        }),
        ('Статистика', {
            'fields': ('students_count_display',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    inlines = [ReTrainingStudentInline, AssignmentInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher', 'language',
        ).prefetch_related('retraining_students')

    def students_count_display(self, obj):
        count = obj.retraining_students.count()
        if count >= obj.max_students:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}/{}</span>',
                count, obj.max_students
            )
        elif count >= obj.max_students * 0.8:  # 80% заполненности
            return format_html(
                '<span style="color: orange; font-weight: bold;">{}/{}</span>',
                count, obj.max_students
            )
        else:
            return format_html(
                '<span style="color: green;">{}/{}</span>',
                count, obj.max_students
            )

    students_count_display.short_description = 'Студенты'

    def view_students_link(self, obj):
        count = obj.students.count()
        if count > 0:
            url = reverse('admin:retraining_retrainingstudent_changelist')
            return format_html(
                '<a href="{}?group__id__exact={}">{} студентов</a>',
                url, obj.id, count
            )
        return "Нет студентов"

    view_students_link.short_description = 'Студенты'

    actions = ['duplicate_groups']

    def duplicate_groups(self, request, queryset):
        count = 0
        for group in queryset:
            group.pk = None
            group.name = f"{group.name} (копия)"
            group.save()
            count += 1
        self.message_user(request, f'{count} групп скопировано.')

    duplicate_groups.short_description = 'Создать копии выбранных групп'


@admin.register(ReTrainingStudent)
class ReTrainingStudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'student_id_number', 'group',
        'enrolled_at', 'days_in_course'
    ]
    list_filter = [
        'group', 'enrolled_at'
    ]
    search_fields = [
        'student__full_name', 'student__student_id_number',
        'student__email', 'group__name'
    ]
    readonly_fields = ['enrolled_at', 'days_in_course']

    fieldsets = (
        ('Основная информация', {
            'fields': ('student', 'group')
        }),
        ('Даты', {
            'fields': ('enrolled_at', 'days_in_course')
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'group'
        )

    def student_name(self, obj):
        if obj.student:
            return obj.student.full_name
        return "Неизвестно"

    student_name.short_description = 'Имя студента'
    student_name.admin_order_field = 'student__full_name'

    def student_id_number(self, obj):
        if obj.student:
            return obj.student.student_id_number
        return "Неизвестно"

    student_id_number.short_description = 'ID студента'
    student_id_number.admin_order_field = 'student__student_id_number'

    def days_in_course(self, obj):
        if obj.enrolled_at:
            delta = timezone.now() - obj.enrolled_at
            return f"{delta.days} дней"
        return "-"

    days_in_course.short_description = 'В курсе'

    actions = ['move_to_group']

    def move_to_group(self, request, queryset):
        # Здесь можно добавить логику для перевода студентов в другую группу
        self.message_user(request, 'Для перевода студентов в другую группу используйте форму редактирования.')

    move_to_group.short_description = 'Перевести в другую группу'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'assignment_type', 'group', 'status', 'created_by',
        'start_datetime', 'end_datetime', 'question_count', 'max_attempts',
        'submissions_count_display', 'assignment_is_active'
    ]
    list_filter = [
        'assignment_type', 'status', 'group', 'created_by',
        'start_datetime', 'created_at', 'enable_proctoring'
    ]
    search_fields = ['title', 'description', 'group__name']
    readonly_fields = [
        'question_count', 'submissions_count_display', 'completed_submissions_count_display',
        'assignment_is_active', 'assignment_is_completed', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'assignment_type', 'status')
        }),
        ('Параметры', {
            'fields': ('group', 'created_by', 'max_attempts', 'question_count')
        }),
        ('Время', {
            'fields': ('start_datetime', 'end_datetime', 'duration_minutes')
        }),
        ('Файл задания', {
            'fields': ('assignment_file',),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': (
                'show_results_immediately', 'randomize_questions',
                'enable_proctoring'
            ),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': (
                'submissions_count_display', 'completed_submissions_count_display',
                'assignment_is_active', 'assignment_is_completed'
            ),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [TestQuestionInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'group', 'created_by'
        ).prefetch_related('questions', 'submissions')

    def submissions_count_display(self, obj):
        count = obj.submissions.count()
        if count > 0:
            url = reverse('admin:retraining_assignmentsubmission_changelist')
            return format_html(
                '<a href="{}?assignment__id__exact={}">{} сдач</a>',
                url, obj.id, count
            )
        return "0 сдач"

    submissions_count_display.short_description = 'Сдачи'

    def completed_submissions_count_display(self, obj):
        return obj.completed_submissions_count

    completed_submissions_count_display.short_description = 'Завершенные сдачи'

    def assignment_is_active(self, obj):
        return obj.is_active

    assignment_is_active.short_description = 'Активно'
    assignment_is_active.boolean = True

    def assignment_is_completed(self, obj):
        return obj.is_completed

    assignment_is_completed.short_description = 'Завершено'
    assignment_is_completed.boolean = True

    def get_inline_instances(self, request, obj=None):
        """Показывать inline только для тестов"""
        if obj and obj.assignment_type == 'test':
            return super().get_inline_instances(request, obj)
        return []

    actions = ['publish_assignments', 'activate_assignments', 'complete_assignments']

    def publish_assignments(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} заданий опубликовано.')

    publish_assignments.short_description = 'Опубликовать выбранные задания'

    def activate_assignments(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} заданий активировано.')

    activate_assignments.short_description = 'Активировать выбранные задания'

    def complete_assignments(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заданий завершено.')

    complete_assignments.short_description = 'Пометить как завершенные'


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = [
        'question_text_short', 'assignment', 'question_type',
        'points', 'order', 'is_required', 'is_active'
    ]
    list_filter = ['question_type', 'assignment', 'is_required', 'is_active']
    search_fields = ['question_text', 'assignment__title']
    ordering = ['assignment', 'order']

    fieldsets = (
        ('Основная информация', {
            'fields': ('assignment', 'question_text', 'question_type')
        }),
        ('Параметры', {
            'fields': ('points', 'order', 'is_required', 'is_active')
        }),
        ('Правильный ответ', {
            'fields': ('correct_answer',),
            'description': 'Заполните для текстовых и числовых вопросов'
        })
    )

    inlines = [TestQuestionOptionInline]

    def question_text_short(self, obj):
        return f"{obj.question_text[:50]}..." if len(obj.question_text) > 50 else obj.question_text

    question_text_short.short_description = 'Текст вопроса'

    def get_inline_instances(self, request, obj=None):
        """Показывать варианты ответов только для вопросов с выбором"""
        if obj and obj.question_type in ['single_choice', 'multiple_choice']:
            return super().get_inline_instances(request, obj)
        return []

    actions = ['duplicate_questions', 'activate_questions', 'deactivate_questions']

    def duplicate_questions(self, request, queryset):
        count = 0
        for question in queryset:
            # Сохраняем варианты ответов
            options = list(question.options.all())

            # Дублируем вопрос
            question.pk = None
            question.question_text = f"{question.question_text} (копия)"
            question.save()

            # Дублируем варианты ответов
            for option in options:
                option.pk = None
                option.question = question
                option.save()

            count += 1
        self.message_user(request, f'{count} вопросов скопировано.')

    duplicate_questions.short_description = 'Создать копии вопросов'

    def activate_questions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} вопросов активировано.')

    activate_questions.short_description = 'Активировать вопросы'

    def deactivate_questions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} вопросов деактивировано.')

    deactivate_questions.short_description = 'Деактивировать вопросы'


@admin.register(TestQuestionOption)
class TestQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['option_text_short', 'question', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__assignment']
    search_fields = ['option_text', 'question__question_text']
    ordering = ['question', 'order']

    def option_text_short(self, obj):
        return f"{obj.option_text[:50]}..." if len(obj.option_text) > 50 else obj.option_text

    option_text_short.short_description = 'Текст варианта'


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'assignment_title', 'assignment_type', 'status',
        'attempt_number', 'started_at', 'completed_at', 'grade', 'percentage_score_display'
    ]
    list_filter = [
        'status', 'assignment__assignment_type', 'assignment',
        'started_at', 'completed_at', 'graded_at'
    ]
    search_fields = [
        'student__student__full_name', 'assignment__title',
        'student__student__student_id_number'
    ]
    readonly_fields = [
        'started_at', 'percentage_score_display', 'is_passed_display', 'time_taken_display',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('assignment', 'student', 'status', 'attempt_number')
        }),
        ('Время', {
            'fields': ('started_at', 'completed_at', 'graded_at', 'time_taken_display')
        }),
        ('Результаты', {
            'fields': ('score', 'max_score', 'grade', 'percentage_score_display', 'is_passed_display')
        }),
        ('Файлы и комментарии', {
            'fields': ('submission_file', 'student_comment', 'teacher_comment')
        }),
        ('Дополнительно', {
            'fields': ('graded_by', 'ip_address')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [TestAnswerInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assignment', 'student__student', 'graded_by'
        ).prefetch_related('test_answers')

    def student_name(self, obj):
        return obj.student.student.full_name

    student_name.short_description = 'Студент'
    student_name.admin_order_field = 'student__student__full_name'

    def assignment_title(self, obj):
        return obj.assignment.title

    assignment_title.short_description = 'Задание'
    assignment_title.admin_order_field = 'assignment__title'

    def assignment_type(self, obj):
        return obj.assignment.get_assignment_type_display()

    assignment_type.short_description = 'Тип'

    def percentage_score_display(self, obj):
        return obj.percentage_score

    percentage_score_display.short_description = 'Процент'

    def is_passed_display(self, obj):
        return obj.is_passed

    is_passed_display.short_description = 'Прошел'
    is_passed_display.boolean = True

    def time_taken_display(self, obj):
        return obj.time_taken

    time_taken_display.short_description = 'Время выполнения'

    def get_inline_instances(self, request, obj=None):
        """Показывать ответы только для тестов"""
        if obj and obj.assignment.assignment_type == 'test':
            return super().get_inline_instances(request, obj)
        return []

    def colored_status(self, obj):
        colors = {
            'started': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'graded': 'darkgreen',
            'overdue': 'red'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )

    colored_status.short_description = 'Статус'

    actions = ['mark_as_completed', 'auto_grade', 'export_results']

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{updated} работ помечены как завершенные.')

    mark_as_completed.short_description = 'Пометить как завершенные'

    def auto_grade(self, request, queryset):
        """Автоматическое оценивание для заданий с файлами"""
        count = 0
        for submission in queryset.filter(
                assignment__assignment_type='assignment',
                status='completed'
        ):
            if not submission.grade:
                submission.grade = 75  # Средний балл
                submission.status = 'graded'
                submission.graded_at = timezone.now()
                submission.graded_by = request.user
                submission.save()
                count += 1

        self.message_user(request, f'{count} работ автоматически оценено.')

    auto_grade.short_description = 'Автоматически оценить (75 баллов)'

    def export_results(self, request, queryset):
        """Экспорт результатов в CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="results.csv"'

        writer = csv.writer(response)
        writer.writerow(['Студент', 'Задание', 'Группа', 'Оценка', 'Статус', 'Дата'])

        for submission in queryset:
            writer.writerow([
                submission.student.student.full_name,
                submission.assignment.title,
                submission.assignment.group.name,
                submission.grade or '',
                submission.get_status_display(),
                submission.started_at.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    export_results.short_description = 'Экспортировать результаты в CSV'


@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'submission_student', 'question_short', 'question_type',
        'is_correct', 'points_earned'
    ]
    list_filter = ['is_correct', 'submission__assignment', 'question__question_type']
    search_fields = [
        'submission__student__student__full_name',
        'question__question_text',
        'text_answer'
    ]
    readonly_fields = ['is_correct', 'points_earned']

    def submission_student(self, obj):
        return obj.submission.student.student.full_name

    submission_student.short_description = 'Студент'

    def question_short(self, obj):
        return f"{obj.question.question_text[:30]}..."

    question_short.short_description = 'Вопрос'

    def question_type(self, obj):
        return obj.question.get_question_type_display()

    question_type.short_description = 'Тип вопроса'

    def has_add_permission(self, request):
        return False


# ============================================================================
# НАСТРОЙКИ АДМИНКИ
# ============================================================================

admin.site.site_header = "Система переобучения"
admin.site.site_title = "Переобучение - Админ"
admin.site.index_title = "Панель управления переобучением"


#salom