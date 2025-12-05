"""
Modules app models: Module, UserModuleRole
"""
from django.db import models
from core.models import BaseModel


class Module(BaseModel):
    """Module model for accreditation modules (PHC-LAB, PHC Dental, etc.)."""
    code = models.CharField(max_length=50, unique=True)  # e.g., "PHC-LAB"
    display_name = models.CharField(max_length=255)  # e.g., "PHC Laboratory"
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['display_name']
    
    def __str__(self):
        return f"{self.code} - {self.display_name}"


class UserModuleRole(BaseModel):
    """User role assignment per module."""
    ROLE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),
        ('DASHBOARD_ADMIN', 'Dashboard Admin'),
        ('CATEGORY_ADMIN', 'Category Admin'),
        ('USER', 'User'),
    ]
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='module_roles'
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    categories = models.JSONField(default=list, blank=True)  # List of category codes for CATEGORY_ADMIN
    
    class Meta:
        db_table = 'user_module_roles'
        unique_together = [['user', 'module']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.module.code} ({self.get_role_display()})"
