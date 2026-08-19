
from django.db import models
from django.contrib.auth import get_user_model

from bigbluebutton.models import Bigbluebutton_Model

User = get_user_model()
from speciality.models import Bspeciality
from group.models import Group
from learning_process.models import Educationlang
from universty.models import Faculty
from students.models import Student
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from shared.models import BaseModel


class ReTrainingGroup(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    max_students = models.PositiveIntegerField(default=200)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='retraining_teacher')
    language = models.ForeignKey(Educationlang, on_delete=models.SET_NULL, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True,)
    speciality = models.ForeignKey(Bspeciality, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    min_students = models.PositiveIntegerField(default=10)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    registration_start = models.DateField(null=True, blank=True)
    registration_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    online_room = models.OneToOneField(
    Bigbluebutton_Model,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='retraining_group')

    def __str__(self):
        return self.name


class ReTrainingStudent(BaseModel):
    STATUS_CHOICES = [
        ('registered', 'Зарегистрирован'),
        ('studying', 'Обучается'),
        ('completed', 'Завершил'),
        ('expired', 'Истёк срок'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(ReTrainingGroup, on_delete=models.CASCADE, related_name='retraining_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    enrolled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        unique_together = ('student', 'group')

    def __str__(self):
        return f"{self.student.full_name} -> {self.group.name}"


class Assignment(BaseModel):
    """Модель задания/теста для группы переобучения"""

    TYPE_CHOICES = [
        ('test', 'Тест'),
        ('assignment', 'Задание с файлом'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    # Основная информация
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    assignment_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип задания'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )

    # Связи
    group = models.ForeignKey(
        ReTrainingGroup,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Группа'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_assignments',
        verbose_name='Создал'
    )

    # Временные параметры
    start_datetime = models.DateTimeField(verbose_name='Дата и время начала')
    end_datetime = models.DateTimeField(verbose_name='Дата и время окончания')
    duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name='Продолжительность (минуты)'
    )

    # Параметры задания
    max_attempts = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество попыток'
    )
    question_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество вопросов'
    )

    # Файл задания (только для типа 'assignment')
    assignment_file = models.FileField(
        upload_to='assignments/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'zip', 'rar']
        )],
        verbose_name='Файл задания'
    )

    # Дополнительные настройки
    show_results_immediately = models.BooleanField(
        default=True,
        verbose_name='Показывать результаты сразу'
    )
    randomize_questions = models.BooleanField(
        default=False,
        verbose_name='Случайный порядок вопросов'
    )

    # Настройки прокторинга (интеграция с существующей системой)
    enable_proctoring = models.BooleanField(
        default=False,
        verbose_name='Включить прокторинг'
    )

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.group.name})"

    @property
    def is_active(self):
        """Активно ли задание сейчас"""
        now = timezone.now()
        return (
                self.status == 'active' and
                self.start_datetime <= now <= self.end_datetime
        )

    @property
    def is_published(self):
        """Опубликовано ли задание"""
        return self.status in ['published', 'active']

    @property
    def is_completed(self):
        """Завершено ли задание"""
        return (
                (self.end_datetime is not None and timezone.now() > self.end_datetime)
                or self.status == 'completed'
        )

    @property
    def submissions_count(self):
        """Количество сдач"""
        return self.submissions.count()

    @property
    def completed_submissions_count(self):
        """Количество завершенных сдач"""
        return self.submissions.filter(status='completed').count()

    def activate(self):
        """Активировать задание"""
        if self.status == 'published':
            self.status = 'active'
            self.save()

    def complete(self):
        """Завершить задание"""
        if self.status == 'active':
            self.status = 'completed'
            self.save()


class TestQuestion(BaseModel):
    """Модель вопроса для теста"""

    QUESTION_TYPES = [
        ('single_choice', 'Одиночный выбор'),
        ('multiple_choice', 'Множественный выбор'),
        ('text', 'Текстовый ответ'),
        ('number', 'Числовой ответ'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Задание'
    )

    question_text = models.TextField(verbose_name='Текст вопроса')
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        verbose_name='Тип вопроса'
    )

    # Порядок вопроса
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    # Баллы за правильный ответ
    points = models.PositiveIntegerField(default=1, verbose_name='Баллы')

    # Правильный ответ (для текстовых и числовых вопросов)
    correct_answer = models.TextField(
        blank=True,
        null=True,
        verbose_name='Правильный ответ'
    )

    # Обязательный вопрос
    is_required = models.BooleanField(default=True, verbose_name='Обязательный')
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    class Meta:
        verbose_name = 'Вопрос теста'
        verbose_name_plural = 'Вопросы теста'
        ordering = ['order']

    def __str__(self):
        return f"Вопрос {self.order}: {self.question_text[:50]}..."

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if self.assignment.assignment_type == 'test' and (is_new or 'update_fields' in kwargs):
            self.assignment.question_count = self.assignment.questions.filter(is_active=True).count()
            self.assignment.save(update_fields=['question_count'])


class TestQuestionOption(BaseModel):
    """Модель варианта ответа для вопроса"""

    question = models.ForeignKey(
        TestQuestion,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='Вопрос'
    )

    option_text = models.TextField(verbose_name='Текст варианта')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['order']

    def __str__(self):
        return f"{self.option_text[:50]}..."


class AssignmentSubmission(BaseModel):
    """Модель сдачи задания студентом"""

    STATUS_CHOICES = [
        ('started', 'Начата'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершена'),
        ('graded', 'Оценена'),
        ('overdue', 'Просрочена'),
    ]

    # Основные связи
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Задание'
    )
    student = models.ForeignKey(
        ReTrainingStudent,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Студент'
    )

    # Статус и попытка
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='started',
        verbose_name='Статус'
    )
    attempt_number = models.PositiveIntegerField(
        default=1,
        verbose_name='Номер попытки'
    )

    # Временные метки
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начало')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершение')
    graded_at = models.DateTimeField(null=True, blank=True, verbose_name='Оценено')

    # Результаты
    score = models.FloatField(null=True, blank=True, verbose_name='Баллы')
    max_score = models.FloatField(null=True, blank=True, verbose_name='Максимальные баллы')
    grade = models.FloatField(null=True, blank=True, verbose_name='Оценка')

    # Файл ответа (для заданий с файлом)
    submission_file = models.FileField(
        upload_to='submissions/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'zip', 'rar', 'jpg', 'png']
        )],
        verbose_name='Файл ответа'
    )

    # Комментарии
    student_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий студента'
    )
    teacher_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий преподавателя'
    )

    # Кто оценил
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        verbose_name='Оценил'
    )

    # IP адрес (для безопасности)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP адрес'
    )

    # Данные для тестов (JSON поле для хранения вопросов)
    test_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Данные теста'
    )

    class Meta:
        verbose_name = 'Сдача задания'
        verbose_name_plural = 'Сдачи заданий'
        unique_together = ['assignment', 'student', 'attempt_number']
        ordering = ['-started_at']

    def __str__(self):
        student_name = self.student.student.full_name if self.student and self.student.student else "???"
        assignment_title = self.assignment.title if self.assignment else "???"
        return f"{student_name} - {assignment_title} (попытка {self.attempt_number})"

    @property
    def percentage_score(self):
        """Процент выполнения"""
        if self.score is not None and self.max_score and self.max_score > 0:
            return (self.score / self.max_score) * 100
        return None

    @property
    def is_passed(self):
        """Прошел ли студент задание"""
        percentage = self.percentage_score
        return percentage is not None and percentage >= 60  # 60% - проходной балл

    @property
    def time_taken(self):
        """Время выполнения"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None

    @property
    def is_overdue(self):
        """Просрочено ли задание"""
        if not self.completed_at:
            return timezone.now() > self.assignment.end_datetime
        return False

    def can_attempt(self):
        current_attempts = AssignmentSubmission.objects.filter(
            assignment=self.assignment,
            student=self.student
        ).exclude(pk=self.pk).count()
        return current_attempts < self.assignment.max_attempts


class TestAnswer(BaseModel):
    """Модель ответа студента на вопрос теста"""

    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name='test_answers',
        verbose_name='Сдача'
    )
    question = models.ForeignKey(
        TestQuestion,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name='Вопрос'
    )

    # Ответы
    selected_options = models.ManyToManyField(
        TestQuestionOption,
        blank=True,
        verbose_name='Выбранные варианты'
    )
    text_answer = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текстовый ответ'
    )

    # Результат
    is_correct = models.BooleanField(null=True, blank=True, verbose_name='Правильный')
    points_earned = models.FloatField(default=0, verbose_name='Заработанные баллы')

    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'
        unique_together = ['submission', 'question']

    def __str__(self):
        student_name = self.submission.student.student.full_name if self.submission and self.submission.student else "???"
        question_text = self.question.question_text[:30] if self.question else "???"
        return f"{student_name} - {question_text}..."

    def check_answer(self):
        if not self.question:
            self.is_correct = False
            self.points_earned = 0
            self.save()
            return

        try:
            if self.question.question_type in ['single_choice', 'multiple_choice']:
                correct_ids = set(self.question.options.filter(is_correct=True).values_list('id', flat=True))
                selected_ids = set(self.selected_options.all().values_list('id', flat=True))
                if self.question.question_type == 'single_choice':
                    self.is_correct = len(selected_ids) == 1 and selected_ids == correct_ids
                else:
                    self.is_correct = selected_ids == correct_ids
            elif self.question.question_type in ['text', 'number']:
                if self.text_answer and self.question.correct_answer:
                    if self.question.question_type == 'number':
                        student_answer = float(self.text_answer.strip())
                        correct_answer = float(self.question.correct_answer.strip())
                        self.is_correct = abs(student_answer - correct_answer) < 0.01
                    else:
                        self.is_correct = self.text_answer.strip().lower() == self.question.correct_answer.strip().lower()
                else:
                    self.is_correct = False
            else:
                self.is_correct = False
        except Exception:
            self.is_correct = False

        self.points_earned = self.question.points if self.is_correct else 0
        self.save()
