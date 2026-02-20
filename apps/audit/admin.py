from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_repr', 'ip_address')
    list_filter = ('action', 'timestamp', 'content_type')
    search_fields = ('user__username', 'object_repr', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'content_type', 'object_id', 'object_repr', 'changes', 'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
