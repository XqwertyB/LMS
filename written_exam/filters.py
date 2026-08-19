from django_filters import rest_framework as filters
from written_exam.models import WrittenExam


class WrittenExamFilter(filters.FilterSet):
    search = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains"
    )

    curriculum = filters.UUIDFilter(field_name="curriculum_id")
    subject = filters.UUIDFilter(field_name="subject_id")
    teacher = filters.UUIDFilter(field_name="teacher_id")

    exam_type = filters.CharFilter(field_name="exam_type")
    status = filters.BooleanFilter(field_name="status")

    class Meta:
        model = WrittenExam
        fields = []


class WrittenExamListFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    curriculum = filters.UUIDFilter()

    class Meta:
        model = WrittenExam
        fields = ['name', 'curriculum', ]
