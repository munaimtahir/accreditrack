"""
Accounts app models: User, Role, UserRole
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from core.models import BaseModel


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Custom User model with email as username."""
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email


class Role(BaseModel):
    """Role model for RBAC."""
    ROLE_CHOICES = [
        ('SuperAdmin', 'Super Admin'),
        ('QAAdmin', 'QA Admin'),
        ('DepartmentCoordinator', 'Department Coordinator'),
        ('Viewer', 'Viewer'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'roles'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class UserRole(BaseModel):
    """Many-to-many relationship between User and Role with optional department."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.CASCADE,
        related_name='user_roles',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'user_roles'
        unique_together = [['user', 'role', 'department']]
        ordering = ['-created_at']
    
    def __str__(self):
        dept_str = f" ({self.department.name})" if self.department else ""
        return f"{self.user.email} - {self.role.get_name_display()}{dept_str}"
