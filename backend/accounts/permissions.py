"""
Custom permission classes for RBAC.
"""
from rest_framework import permissions
from .models import Role


class IsQAAdmin(permissions.BasePermission):
    """Permission check for QAAdmin or SuperAdmin."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # SuperAdmin has all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user has QAAdmin role
        return request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()


class IsDepartmentCoordinator(permissions.BasePermission):
    """Permission check for DepartmentCoordinator role."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.user_roles.filter(
            role__name='DepartmentCoordinator'
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        """Check if user is coordinator for the object's department."""
        if request.user.is_superuser:
            return True
        
        # For objects with department attribute
        if hasattr(obj, 'department'):
            return request.user.user_roles.filter(
                role__name='DepartmentCoordinator',
                department=obj.department
            ).exists()
        
        return False
