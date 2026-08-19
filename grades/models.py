from group.models import Group
from semestr.models import Hsemester
from shared.models import BaseModel,models
from learning_process.models import Curriculum
from students.models import Student
from subjects.models import Subject_Curriculum


class ConnectGrades(BaseModel):

    TYPE_GRADE = (
        ("asosiy", "Asosiy natija"),
        ("qayta", "Qayta topshirish"),
    )

    subject = models.ForeignKey(
        Subject_Curriculum,
        on_delete=models.PROTECT,
        related_name="grade_sheets_by_subject"
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="grade_sheets_by_group"
    )

    sheet_type = models.CharField(
        max_length=10,
        choices=TYPE_GRADE,
        default="asosiy"
    )

    class Meta:
        unique_together = (
            "subject",
            "group",
            "sheet_type"
        )

        indexes = [
            models.Index(fields=["subject"]),
            models.Index(fields=["group"]),
        ]

    def __str__(self):
        return f"{self.subject} | {self.group} | {self.semester} | {self.sheet_type}"


class Grade(BaseModel):

    connect_grade = models.ForeignKey(
        ConnectGrades,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="grades"
    )

    jn_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    on_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    yn_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = "student_grades"

        unique_together = (
            "connect_grade",
            "student"
        )

        indexes = [
            models.Index(fields=["connect_grade"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.student} | {self.connect_grade}"