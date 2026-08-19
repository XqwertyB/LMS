import random
from django.core.exceptions import ValidationError
from django.db.models import Count
from .models import WrittenExamQuestion, WrittenExam


def generate_exam_questions(exam: WrittenExam):
    counts = (
        WrittenExamQuestion.objects
        .filter(exam=exam, status=True)
        .values("difficulty")
        .annotate(total=Count("id"))
    )

    count_map = {item["difficulty"]: item["total"] for item in counts}

    easy_available = count_map.get("easy", 0)
    medium_available = count_map.get("medium", 0)
    hard_available = count_map.get("hard", 0)

    if easy_available < exam.easy_count:
        raise ValidationError(
            f"Oson savollar yetarli emas! Kerakli: {exam.easy_count}, mavjud: {easy_available}"
        )

    if medium_available < exam.medium_count:
        raise ValidationError(
            f"O‘rtacha savollar yetarli emas! Kerakli: {exam.medium_count}, mavjud: {medium_available}"
        )

    if hard_available < exam.hard_count:
        raise ValidationError(
            f"Qiyin savollar yetarli emas! Kerakli: {exam.hard_count}, mavjud: {hard_available}"
        )

    # 🔹 DB darajasida random olish (faqat kerakli miqdor)
    easy_questions = list(
        WrittenExamQuestion.objects
        .filter(exam=exam, difficulty="easy", status=True)
        .order_by("?")[:exam.easy_count]
    )

    medium_questions = list(
        WrittenExamQuestion.objects
        .filter(exam=exam, difficulty="medium", status=True)
        .order_by("?")[:exam.medium_count]
    )

    hard_questions = list(
        WrittenExamQuestion.objects
        .filter(exam=exam, difficulty="hard", status=True)
        .order_by("?")[:exam.hard_count]
    )

    selected = easy_questions + medium_questions + hard_questions
    random.shuffle(selected)

    return selected


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    return ip


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomQPageNumberPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        difficulty_counts = getattr(self, "difficulty_counts", {})

        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "page_size": self.get_page_size(self.request),

            "difficulty_counts": {
                "easy": difficulty_counts.get("easy", 0),
                "medium": difficulty_counts.get("medium", 0),
                "hard": difficulty_counts.get("hard", 0),
            },

            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })