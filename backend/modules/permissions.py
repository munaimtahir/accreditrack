"""
Permission classes for modules app.
"""
from rest_framework import permissions
from .models import UserModuleRole


class IsModuleSuperAdmin(permissions.BasePermission):
    """Permission to check if user is SUPERADMIN for a module."""
    
    def has_permission(self, request, view):
        """Check if user has SUPERADMIN role for the module."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        module_id = view.kwargs.get('module_id') or request.data.get('module') or request.query_params.get('module')
        if not module_id:
            return False
        
        return UserModuleRole.objects.filter(
            user=request.user,
            module_id=module_id,
            role='SUPERADMIN'
        ).exists()


class IsModuleDashboardAdmin(permissions.BasePermission):
    """Permission to check if user is DASHBOARD_ADMIN for a module."""
    
    def has_permission(self, request, view):
        """Check if user has DASHBOARD_ADMIN role for the module."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        module_id = view.kwargs.get('module_id') or request.data.get('module') or request.query_params.get('module')
        if not module_id:
            return False
        
        return UserModuleRole.objects.filter(
            user=request.user,
            module_id=module_id,
            role__in=['SUPERADMIN', 'DASHBOARD_ADMIN']
        ).exists()


class IsModuleCategoryAdmin(permissions.BasePermission):
    """Permission to check if user is CATEGORY_ADMIN for a module."""
    
    def has_permission(self, request, view):
        """Check if user has CATEGORY_ADMIN role for the module."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        module_id = view.kwargs.get('module_id') or request.data.get('module') or request.query_params.get('module')
        if not module_id:
            return False
        
        return UserModuleRole.objects.filter(
            user=request.user,
            module_id=module_id,
            role__in=['SUPERADMIN', 'DASHBOARD_ADMIN', 'CATEGORY_ADMIN']
        ).exists()


class IsModuleUser(permissions.BasePermission):
    """Permission to check if user has any role for a module."""
    
    def has_permission(self, request, view):
        """Check if user has any role for the module."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        module_id = view.kwargs.get('module_id') or request.data.get('module') or request.query_params.get('module')
        if not module_id:
            return False
        
        return UserModuleRole.objects.filter(
            user=request.user,
            module_id=module_id
        ).exists()
