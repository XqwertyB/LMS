# services.py
from django.db import transaction
from django.db.models import Sum, Subquery, F, OuterRef, Max, ExpressionWrapper, FloatField

from content.models import Task_students
from exam.models import Result
from written_exam.models import WrittenExamAttempt
from .models import ConnectGrades, Grade



class GradeService:

    @staticmethod
    def create_sheet(subject, group, students):
        connect, _ = ConnectGrades.objects.get_or_create(
            subject_id=subject,
            group_id=group,
            sheet_type="asosiy"
        )

        grades = [
            Grade(connect_grade=connect, student_id=s)
            for s in students
        ]

        Grade.objects.bulk_create(grades, ignore_conflicts=True)
        return connect

    @staticmethod
    def calculate_jn(connect: ConnectGrades):
        sc = connect.subject

        qs = (
            Task_students.objects
            .filter(
                mark_status=True,
                tasks_id__topic_id_task__content_id_topic__subject_id=sc.subject,
                tasks_id__topic_id_task__content_id_topic__curriculum_id=sc.subject_curriculum,
                tasks_id__topic_id_task__content_id_topic__content_semestrs=sc.subject_semestr,
                task_student_id__group=connect.group,
            )
            .values("task_student_id")
            .annotate(jn_score=Sum("mark"))
        )

        grades = [
            Grade(
                connect_grade=connect,
                student_id=row["task_student_id"],
                jn_score=row["jn_score"] or 0
            )
            for row in qs
        ]

        with transaction.atomic():
            Grade.objects.bulk_create(
                grades,
                batch_size=1000,
                update_conflicts=True,
                update_fields=["jn_score"],
                unique_fields=["connect_grade", "student"]
            )

        return len(grades)



def calculate_on(connect: ConnectGrades):
    sc = connect.subject

    # 1. Asosiy filter
    base_qs = WrittenExamAttempt.objects.filter(
        exam__exam_type="midterm",
        status="submitted",
        exam__subject=sc.subject,
        exam__curriculum=sc.subject_curriculum,
        exam__assigned_exams__group=connect.group,
    ).distinct()

    # 2. Har student uchun oxirgi attempt
    latest_attempt_subquery = (
        base_qs
        .filter(student=OuterRef("student"))
        .order_by("-attempt_no")
        .values("attempt_no")[:1]
    )

    latest_attempts = (
        base_qs
        .annotate(latest_attempt_no=Subquery(latest_attempt_subquery))
        .filter(attempt_no=F("latest_attempt_no"))
    )

    # 3. Ballarni hisoblash
    latest_attempts = latest_attempts.annotate(
        calculated_score=Sum("answers__score")
    )

    # 4. Grade ro'yxatini tayyorlash
    grades = [
        Grade(
            connect_grade=connect,
            student_id=item.student_id,
            on_score=item.calculated_score or 0
        )
        for item in latest_attempts
    ]

    # 5. Bulk upsert
    if grades:
        with transaction.atomic():
            Grade.objects.bulk_create(
                grades,
                batch_size=1000,
                update_conflicts=True,
                update_fields=["on_score"],
                unique_fields=["connect_grade", "student"]
            )

    return len(grades)

def calculate_yn(connect: ConnectGrades):
    sc = connect.subject

    # 1. BASE FILTER
    base_qs = Result.objects.filter(
        exam__subject=sc.subject,
        exam__curriculum=sc.subject_curriculum,
        exam__semester=sc.subject_semestr,
        group=connect.group,
    )

    # 2. har student uchun oxirgi attempt
    latest_attempts = (
        base_qs
        .values("student")
        .annotate(last_attempt=Max("attempts"))
    )

    # 3. score hisoblash
    results = (
        base_qs
        .annotate(
            score=ExpressionWrapper(
                F("max_score") * F("correct_answer") / F("total_count"),
                output_field=FloatField()
            )
        )
    )

    # 4. map
    score_map = {
        (r.student_id, r.attempts): r.score or 0
        for r in results
    }

    # 5. final list
    grades = []
    for row in latest_attempts:
        student_id = row["student"]
        attempt = row["last_attempt"]

        score = score_map.get((student_id, attempt), 0)

        grades.append(
            Grade(
                connect_grade=connect,
                student_id=student_id,
                yn_score=score
            )
        )

    # 6. bulk update
    with transaction.atomic():
        Grade.objects.bulk_create(
            grades,
            batch_size=1000,
            update_conflicts=True,
            update_fields=["yn_score"],
            unique_fields=["connect_grade", "student"]
        )

    return len(grades)