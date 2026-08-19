import django_filters
from .models import Group


class GroupListFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    group_curriculum = django_filters.UUIDFilter()
    educationLang = django_filters.UUIDFilter()

    class Meta:
        model = Group
        fields = ['id', 'name', 'group_curriculum', 'educationLang']
