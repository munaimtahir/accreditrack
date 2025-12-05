"""
Serializers for organizations app.
"""
from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    parent_name = serializers.CharField(source='parent.name', read_only=True, required=False)
    parent_code = serializers.CharField(source='parent.code', read_only=True, required=False)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'parent_code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
