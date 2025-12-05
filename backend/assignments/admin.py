from django.contrib import admin
from .models import Assignment, ItemStatus, AssignmentUpdate


class ItemStatusInline(admin.TabularInline):
    """Inline admin for ItemStatus."""
    model = ItemStatus
    extra = 0
    readonly_fields = ['last_updated_by', 'last_updated_at']
    fields = ['proforma_item', 'status', 'completion_percent', 'last_updated_by', 'last_updated_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin interface for Assignment model."""
    list_display = ['proforma_template', 'department', 'status', 'start_date', 'due_date', 'created_at']
    list_filter = ['status', 'proforma_template', 'department', 'created_at']
    search_fields = ['proforma_template__title', 'department__name']
    autocomplete_fields = ['proforma_template', 'department']
    inlines = [ItemStatusInline]


@admin.register(ItemStatus)
class ItemStatusAdmin(admin.ModelAdmin):
    """Admin interface for ItemStatus model."""
    list_display = ['assignment', 'proforma_item', 'status', 'completion_percent', 'last_updated_by', 'last_updated_at']
    list_filter = ['status', 'assignment__proforma_template', 'assignment__department', 'created_at']
    search_fields = ['assignment__proforma_template__title', 'proforma_item__code', 'proforma_item__requirement_text']
    autocomplete_fields = ['assignment', 'proforma_item', 'last_updated_by']


@admin.register(AssignmentUpdate)
class AssignmentUpdateAdmin(admin.ModelAdmin):
    """Admin interface for AssignmentUpdate model."""
    list_display = ['assignment', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['assignment__proforma_template__title', 'user__email', 'note']
    autocomplete_fields = ['assignment', 'user']
    readonly_fields = ['created_at', 'updated_at']
