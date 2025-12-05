"""
Views for modules app.
"""
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Module, UserModuleRole
from .serializers import (
    ModuleSerializer,
    UserModuleRoleSerializer,
    UserModuleRoleCreateSerializer
)
from accounts.permissions import IsQAAdmin


class ModuleViewSet(viewsets.ModelViewSet):
    """ViewSet for Module CRUD operations."""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Override to allow read access to all authenticated users."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsQAAdmin()]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(code__icontains=search) |
                models.Q(display_name__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        return queryset


class UserModuleRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for UserModuleRole CRUD operations."""
    queryset = UserModuleRole.objects.select_related('user', 'module').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializer for create/update."""
        if self.action in ['create', 'update', 'partial_update']:
            return UserModuleRoleCreateSerializer
        return UserModuleRoleSerializer
    
    def get_permissions(self):
        """Override to allow read access to all authenticated users."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsQAAdmin()]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        module_id = self.request.query_params.get('module')
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset
