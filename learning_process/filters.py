import django_filters
from .models import Curriculum


class CurriculumFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Curriculum
        fields = ['name', 'educationyear']
