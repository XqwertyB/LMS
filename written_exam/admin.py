from django.contrib import admin
from django.db.models import Count

from .models import AttemptQuestion
from .models import ExamSession
from .models import QuestionBank
from .models import QuestionCollection
from .models import WrittenExam
from .models import WrittenExamAccess
from .models import WrittenExamAnswer
from .models import WrittenExamAttempt
from .models import WrittenExamGroup
from .models import WrittenExamQuestion


@admin.register(QuestionCollection)
class QuestionCollectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_by",
        "question_count",
        "is_deleted",
    )
    list_filter = ("is_deleted", "created_by")
    search_fields = ("name",)
    ordering = ("-id",)
    list_select_related = ("created_by",)
    list_per_page = 50

    actions = ["soft_delete_collections", "restore_collections"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(q_count=Count("questions"))

    def question_count(self, obj):
        return obj.q_count

    question_count.short_description = "Savollar soni"

    def soft_delete_collections(self, request, queryset):
        queryset.update(is_deleted=True)

    soft_delete_collections.short_description = "Tanlangan bazalarni soft-delete qilish"

    def restore_collections(self, request, queryset):
        queryset.update(is_deleted=False)

    restore_collections.short_description = "Tanlangan bazalarni tiklash"


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_text",
        "collection",
        "difficulty",
        "status",
        "is_deleted",
    )
    list_filter = (
        "difficulty",
        "status",
        "is_deleted",
        "collection",
    )
    search_fields = ("text",)
    ordering = ("-id",)
    list_select_related = ("collection",)
    list_per_page = 50

    actions = ["soft_delete_questions", "restore_questions"]

    def short_text(self, obj):
        return obj.text[:60]

    short_text.short_description = "Savol matni"

    def soft_delete_questions(self, request, queryset):
        queryset.update(is_deleted=True)

    soft_delete_questions.short_description = "Tanlangan savollarni soft-delete qilish"

    def restore_questions(self, request, queryset):
        queryset.update(is_deleted=False)

    restore_questions.short_description = "Tanlangan savollarni tiklash"


# ===============================
# INLINES (minimal & fast)
# ===============================

class WrittenExamGroupInline(admin.TabularInline):
    model = WrittenExamGroup
    extra = 0
    autocomplete_fields = ("group",)
    show_change_link = True


# ===============================
# WRITTEN EXAM ADMIN
# ===============================

@admin.register(WrittenExam)
class WrittenExamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "subject",
        "teacher",
        "grader",
        "exam_type",
        "begin_time",
        "end_time",
        "status",
        "created_at",
    )

    list_filter = (
        "exam_type",
        "status",
        "subject",
        "teacher",
    )

    search_fields = (
        "name",
        "subject__name",
        "teacher__full_name",
    )

    date_hierarchy = "begin_time"

    readonly_fields = ("created_by",)

    # 🚀 FK dropdownlarni tezlashtiradi
    autocomplete_fields = ("subject", "teacher")

    # 🚀 og‘ir inline’larni olib tashladik
    inlines = [
        WrittenExamGroupInline,
    ]

    # 🚀 N+1 querylarni yo‘q qiladi
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "subject",
            "teacher",
        )


# ===============================
# QUESTIONS ADMIN
# ===============================

@admin.register(WrittenExamQuestion)
class WrittenExamQuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "exam", "difficulty", "status")
    list_filter = ("difficulty", "status")
    search_fields = ("text", "exam__name")
    autocomplete_fields = ("exam",)

    def short_text(self, obj):
        return obj.text[:60]

    short_text.short_description = "Savol"


# ===============================
# ACCESS ADMIN
# ===============================

@admin.register(WrittenExamAccess)
class WrittenExamAccessAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "is_accessible")
    list_filter = ("is_accessible",)
    search_fields = ("student__full_name",)
    autocomplete_fields = ("exam", "student")


# ===============================
# ATTEMPTS ADMIN
# ===============================

@admin.register(WrittenExamAttempt)
class WrittenExamAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "exam",
        "attempt_no",
        "status",
        "total_score",
        "started_at",
        "is_fully_graded",
    )

    list_filter = ("status", "exam")
    search_fields = ("student__full_name",)
    autocomplete_fields = ("student", "exam")

    readonly_fields = ("started_at", "submitted_at")

    date_hierarchy = "started_at"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "student",
            "exam",
        )


# ===============================
# SESSION ADMIN
# ===============================

@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = (
        "attempt",
        "device_hash",
        "status",
        "locked",
        "last_activity",
    )

    list_filter = ("status", "locked")
    search_fields = ("attempt__student__full_name",)
    autocomplete_fields = ("attempt",)


# ===============================
# ATTEMPT QUESTIONS ADMIN
# ===============================

@admin.register(AttemptQuestion)
class AttemptQuestionAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "order")
    search_fields = ("attempt__student__full_name",)
    autocomplete_fields = ("attempt", "question")
    ordering = ("order",)


# ===============================
# ANSWERS ADMIN
# ===============================

@admin.register(WrittenExamAnswer)
class WrittenExamAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "attempt",
        "question",
        "is_checked",
        "score",
    )

    search_fields = ("attempt__student__full_name",)
    autocomplete_fields = ("attempt", "question")
