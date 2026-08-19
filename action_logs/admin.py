from django.contrib import admin
from action_logs.models import APILogsModel


@admin.register(APILogsModel)
class APILogsAdmin(admin.ModelAdmin):
    """
    Clean, read-only admin for API logs
    """

    list_display = (
        'id',
        'api',
        'method',
        'status_code',
        'execution_time',
        'added_on',
        'user',
    )

    list_filter = (
        'method',
        'status_code',
        'added_on',
        'user',
    )

    search_fields = (
        'api',
        'body',
        'response',
        'headers',
        'client_ip_address',
    )

    readonly_fields = (
        'api',
        'headers',
        'body',
        'method',
        'client_ip_address',
        'response',
        'status_code',
        'execution_time',
        'instance_before_change',
        'added_on',
        'user',
    )

    ordering = ('-added_on',)
    list_per_page = 50
    date_hierarchy = 'added_on'

    # 🔒 AUDIT LOG = READ ONLY
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
