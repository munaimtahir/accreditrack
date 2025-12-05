"""
Serializers for modules app.
"""
from rest_framework import serializers
from .models import Module, UserModuleRole


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module model."""
    
    class Meta:
        model = Module
        fields = ['id', 'code', 'display_name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserModuleRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserModuleRole model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    module_display_name = serializers.CharField(source='module.display_name', read_only=True)
    
    class Meta:
        model = UserModuleRole
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'module', 'module_code', 
            'module_display_name', 'role', 'categories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserModuleRoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating UserModuleRole."""
    
    class Meta:
        model = UserModuleRole
        fields = ['user', 'module', 'role', 'categories']
