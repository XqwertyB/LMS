import django_filters
from .models import Exam


class ExamListFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    curriculum = django_filters.UUIDFilter()
    education_year = django_filters.UUIDFilter()

    class Meta:
        model = Exam
        fields = ['name', 'curriculum', 'education_year']
