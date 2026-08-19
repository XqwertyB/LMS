from django.contrib import admin
from .models import WatchLog
# Register your models here.
@admin.register(WatchLog)
class WatchLogAdmin(admin.ModelAdmin):
    """Watch Log admin"""
    list_display = ('created', 'is_authenticated', 'user', 'ip')
    list_filter = ('is_authenticated', 'created')
    search_fields = ('user',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False