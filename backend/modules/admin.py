"""
Admin configuration for modules app.
"""
from django.contrib import admin
from .models import Module, UserModuleRole


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin interface for Module model."""
    list_display = ['code', 'display_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'display_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(UserModuleRole)
class UserModuleRoleAdmin(admin.ModelAdmin):
    """Admin interface for UserModuleRole model."""
    list_display = ['user', 'module', 'role', 'created_at']
    list_filter = ['role', 'module', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'module__code', 'module__display_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
