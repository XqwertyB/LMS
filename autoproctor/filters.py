import django_filters
from .models import ScreenModel


class ScreenModelFilter(django_filters.FilterSet):
    student_name = django_filters.CharFilter(field_name='student__full_name', lookup_expr='icontains')
    exam_name = django_filters.CharFilter(field_name='exam__name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = ScreenModel
        fields = ['student_name', 'exam_name', 'is_active']
