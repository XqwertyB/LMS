import django_filters
from .models import Faculty, Department


class FacultyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Faculty
        fields = ['name', 'faculty_type']


class DepartmentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    faculty_name = django_filters.CharFilter(field_name='faculty__name', lookup_expr='icontains')
    faculty = django_filters.UUIDFilter()

    class Meta:
        model = Department
        fields = ['name', 'faculty', 'faculty_name']
