from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""
    list_display = ['code', 'name', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'code']
    autocomplete_fields = ['parent']
