from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from group.models import Group
from learning_process.models import Curriculum
from shared.models import BaseModel
from students.models import Student
from subjects.models import Subject
from user.models import User


class QuestionCollection(BaseModel):
    name = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_collections"
    )

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "O'qituvchining savollar bazasi"
        verbose_name_plural = "O'qituvchilarning savollar bazalari"
        indexes = [
            models.Index(fields=['is_deleted']),
            models.Index(fields=['created_by']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'created_by'],
                name='unique_collection_per_user'
            )
        ]


class QuestionBank(BaseModel):
    DIFFICULTY = (
        ('easy', 'Oson'),
        ('medium', 'O‘rtacha'),
        ('hard', 'Qiyin'),
    )
    collection = models.ForeignKey(
        QuestionCollection,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Savol bazasi nomi"
    )

    text = models.TextField(verbose_name="Savol matni")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY)
    status = models.BooleanField(default=True, verbose_name="Faol")

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        indexes = [
            models.Index(fields=['difficulty', 'status', 'is_deleted']),
        ]


class WrittenExam(BaseModel):
    """
    Yozma imtihon
    """

    EXAM_TYPE = (
        ('midterm', 'Oraliq nazorat'),
        ('final', 'Yakuniy nazorat'),
    )

    name = models.CharField(max_length=150, verbose_name="Imtihon nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")

    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE, verbose_name="Imtihon turi")

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name='written_exams',
        verbose_name="O‘quv reja"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='written_exams',
        verbose_name="Fan"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='authored_written_exams',
        verbose_name="Mas'ul o‘qituvchi"
    )

    grader = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='grading_written_exams',
        verbose_name="Tekshiruvchi o‘qituvchi"
    )

    begin_time = models.DateTimeField(verbose_name="Boshlanish vaqti")
    end_time = models.DateTimeField(verbose_name="Tugash vaqti")

    duration_minutes = models.PositiveIntegerField(verbose_name="Ajratilgan vaqt (daqiqada)")
    inactivity_timeout_minutes = models.PositiveIntegerField(default=30, verbose_name="Faollik timeout")

    max_attempts = models.PositiveIntegerField(default=1, verbose_name="Maksimal urinishlar")
    max_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Maksimal ball"
    )

    easy_count = models.PositiveIntegerField(verbose_name="Oson savollar")
    medium_count = models.PositiveIntegerField(verbose_name="O‘rtacha savollar")
    hard_count = models.PositiveIntegerField(verbose_name="Qiyin savollar")
    easy_total_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)
    medium_total_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)
    hard_total_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)
    shuffle_questions = models.BooleanField(default=True, verbose_name="Savollarni aralashtirish")
    status = models.BooleanField(default=False, verbose_name="Faol")

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_written_exams',
        verbose_name="Yaratgan admin"
    )

    class Meta:
        verbose_name = "Yozma imtihon"
        verbose_name_plural = "Yozma imtihonlar"
        indexes = [
            models.Index(fields=['status', '-begin_time']),

            models.Index(fields=['curriculum', 'subject']),

            models.Index(fields=['teacher', 'status']),

            models.Index(fields=['begin_time']),

            models.Index(fields=['end_time']),
        ]
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['curriculum', 'subject', 'exam_type', 'begin_time'],
        #         name='unique_exam_instance'
        #     ),
        # ]

    @property
    def is_editable(self):
        from django.utils import timezone
        now = timezone.now()
        return (
                not self.status and
                self.begin_time > now and
                not self.attempts.exists()
        )

    def clean(self):
        if self.begin_time >= self.end_time:
            raise ValidationError("Boshlanish vaqti tugash vaqtidan oldin bo‘lishi kerak")

        if self.total_questions <= 0:
            raise ValidationError("Savollar soni 0 bo‘lishi mumkin emas")

        total = (
                self.easy_total_score +
                self.medium_total_score +
                self.hard_total_score
        )

        if total != self.max_score:
            raise ValidationError(
                f"Umumiy ball ({self.max_score}) "
                f"= easy+medium+hard ({total}) bo‘lishi kerak"
            )

        # ❗ har biri savol soniga mos bo‘lishi kerak
        if self.easy_count > 0:
            if self.easy_total_score / self.easy_count <= 0:
                raise ValidationError("Easy score noto‘g‘ri")

        if self.medium_count > 0:
            if self.medium_total_score / self.medium_count <= 0:
                raise ValidationError("Medium score noto‘g‘ri")

        if self.hard_count > 0:
            if self.hard_total_score / self.hard_count <= 0:
                raise ValidationError("Hard score noto‘g‘ri")

    @property
    def total_questions(self):
        return self.easy_count + self.medium_count + self.hard_count

    def __str__(self):
        return self.name


class WrittenExamGroup(BaseModel):
    exam = models.ForeignKey(
        WrittenExam,
        on_delete=models.CASCADE,
        related_name='assigned_exams',
        verbose_name="Imtihon"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='exam_assignments',
        verbose_name="Guruh"
    )

    class Meta:
        verbose_name = "Imtihon guruhi"
        verbose_name_plural = "Imtihon guruhlari"
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'group'],
                name='unique_exam_group'
            ),
        ]
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['exam']),
        ]

    def __str__(self):
        return f"{self.exam} — {self.group}"

    # def clean(self):
    #     exists = WrittenExamGroup.objects.filter(
    #         group=self.group,
    #         exam__curriculum=self.exam.curriculum,
    #         exam__subject=self.exam.subject,
    #         exam__exam_type=self.exam.exam_type,
    #         exam__begin_time=self.exam.begin_time,
    #     ).exclude(pk=self.pk).exists()
    #
    #     if exists:
    #         raise ValidationError(
    #             "Bu group uchun shu vaqtda shu turdagi imtihon mavjud"
    #         )

class WrittenExamAccess(BaseModel):
    exam = models.ForeignKey(
        WrittenExam,
        on_delete=models.CASCADE,
        related_name='access_list',
        verbose_name="Imtihon"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='exam_access',
        verbose_name="Talaba"
    )

    is_accessible = models.BooleanField(default=True, verbose_name="Ruxsat berilgan")

    class Meta:
        verbose_name = "Talaba ruxsati"
        verbose_name_plural = "Talabalar ruxsatlari"
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'student'],
                name='unique_exam_student'
            ),
        ]
        indexes = [
            models.Index(fields=["student", "exam"]),
        ]

    def __str__(self):
        return f"{self.student}"


class WrittenExamQuestion(BaseModel):
    DIFFICULTY = (
        ('easy', 'Oson'),
        ('medium', 'O‘rtacha'),
        ('hard', 'Qiyin'),
    )

    exam = models.ForeignKey(
        WrittenExam,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Imtihon"
    )
    question_bank = models.ForeignKey(
        QuestionBank,
        on_delete=models.PROTECT,
        related_name="exam_usages"
    )
    text = models.TextField(verbose_name="Savol matni")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, verbose_name="Qiyinlik darajasi")
    status = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Yozma imtihonga tushgan savol"
        verbose_name_plural = "Yozma imtihonga tushgan savollar"
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'question_bank'],
                name='unique_question_question_bank_per_exam'
            )
        ]

        indexes = [
            models.Index(fields=['exam', 'difficulty', 'status']),
        ]

    def __str__(self):
        return f"{self.exam.name} | {self.get_difficulty_display()}"


class WrittenExamAttempt(BaseModel):
    STATUS = (
        ('in_progress', 'Jarayonda'),
        ('submitted', 'Yakunlangan'),
        ('expired', 'Vaqti tugagan'),
        ('terminated', 'To‘xtatilgan'),
    )

    exam = models.ForeignKey(
        WrittenExam,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Imtihon"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='exam_attempts',
        verbose_name="Talaba"
    )

    attempt_no = models.PositiveIntegerField(verbose_name="Urinish raqami")

    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Boshlangan")
    expires_at = models.DateTimeField(verbose_name="Imtihon tugash vaqti")

    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Talaba topshirgan vaqti")
    graded_at = models.DateTimeField(null=True, blank=True, verbose_name="Baholangan vaqt")

    status = models.CharField(max_length=15, choices=STATUS, default='in_progress', verbose_name="Holati")

    device_fingerprint = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Imtihon urinishi"
        verbose_name_plural = "Imtihon urinishlari"
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'student', 'attempt_no'],
                name='unique_attempt'
            ),
        ]
        indexes = [
            models.Index(fields=['exam', 'student']),
            models.Index(fields=['status']),
            models.Index(fields=['exam', 'student', '-attempt_no'])
        ]

    def __str__(self):
        return f"{self.student.full_name} ({self.attempt_no})"

    @property
    def total_score(self):
        total = self.answers.aggregate(total=Sum('score'))['total']
        return total or Decimal("0.00")

    @property
    def is_fully_graded(self):
        total_questions = self.questions.count()
        graded_answers = self.answers.filter(score__isnull=False).count()
        return total_questions > 0 and total_questions == graded_answers


class ExamSession(BaseModel):
    attempt = models.OneToOneField(
        WrittenExamAttempt,
        on_delete=models.CASCADE,
        related_name='session',
        verbose_name="Urinish"
    )

    device_hash = models.CharField(max_length=255, verbose_name="Qurilma hash")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Oxirgi faollik")

    status = models.BooleanField(default=True, verbose_name="Faol")
    locked = models.BooleanField(default=False, verbose_name="Qurilma bloklangan")

    allow_device_reset = models.BooleanField(
        default=False,
        verbose_name="Qurilma almashtirishga ruxsat"
    )

    class Meta:
        verbose_name = "Imtihon sessiyasi"
        verbose_name_plural = "Imtihon sessiyalari"

    def __str__(self):
        return f"Session {self.attempt_id}"


class AttemptQuestion(BaseModel):
    attempt = models.ForeignKey(
        WrittenExamAttempt,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Urinish"
    )
    question = models.ForeignKey(
        WrittenExamQuestion,
        on_delete=models.CASCADE,
        verbose_name="Savol"
    )

    order = models.PositiveIntegerField(verbose_name="Tartib")

    class Meta:
        verbose_name = "Urinish savoli"
        verbose_name_plural = "Urinish savollari"
        constraints = [
            models.UniqueConstraint(
                fields=['attempt', 'question'],
                name='unique_attempt_question'
            ),
            models.UniqueConstraint(
                fields=['attempt', 'order'],
                name='unique_attempt_order'
            ),
        ]
        ordering = ['order']
        indexes = [
            models.Index(fields=['attempt', 'order']),
        ]

    def __str__(self):
        return f"{self.attempt_id} - {self.order}"


class WrittenExamAnswer(BaseModel):
    attempt = models.ForeignKey(
        WrittenExamAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Urinish"
    )
    question = models.ForeignKey(
        WrittenExamQuestion,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Savol"
    )

    answer_text = models.TextField(blank=True,null=True, verbose_name="Talaba javobi")
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Berilgan ball"
    )
    comment = models.TextField(blank=True,null=True, verbose_name="Oq`ttuvchi izohi")
    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"
        constraints = [
            models.UniqueConstraint(
                fields=['attempt', 'question'],
                name='unique_answer'
            ),
        ]
        indexes = [
            models.Index(fields=["attempt", "question"])
        ]

    def __str__(self):
        return f"{self.attempt.id} - {self.question.id}"

    @property
    def is_checked(self):
        return self.score is not None

    def clean(self):
        super().clean()

        if self.score is None:
            return

        if self.score < Decimal("0"):
            raise ValidationError("Ball manfiy bo‘lishi mumkin emas.")

        exam = self.attempt.exam
        max_score = exam.max_score

        used_score = (
                WrittenExamAnswer.objects
                .filter(attempt=self.attempt)
                .exclude(pk=self.pk)
                .aggregate(total=Sum("score"))["total"]
                or Decimal("0.00")
        )

        remaining_score = max_score - used_score

        if self.score > remaining_score:
            raise ValidationError(
                f"Maksimal qo‘yiladigan ball: {remaining_score}"
            )