from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = ['email', 'full_name', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for UserRole model."""
    list_display = ['user', 'role', 'department', 'created_at']
    list_filter = ['role', 'department', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'role__name', 'department__name']
    autocomplete_fields = ['user', 'role', 'department']
