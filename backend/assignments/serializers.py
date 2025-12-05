"""
Serializers for assignments app.
"""
from rest_framework import serializers
from .models import Assignment, ItemStatus
from proformas.serializers import ProformaTemplateSerializer
from organizations.serializers import DepartmentSerializer


class ItemStatusSerializer(serializers.ModelSerializer):
    """Serializer for ItemStatus model."""
    proforma_item_code = serializers.CharField(source='proforma_item.code', read_only=True)
    proforma_item_text = serializers.CharField(source='proforma_item.requirement_text', read_only=True)
    last_updated_by_email = serializers.CharField(source='last_updated_by.email', read_only=True)
    
    class Meta:
        model = ItemStatus
        fields = [
            'id', 'assignment', 'proforma_item', 'proforma_item_code', 'proforma_item_text',
            'status', 'completion_percent', 'last_updated_by', 'last_updated_by_email',
            'last_updated_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_updated_at', 'created_at', 'updated_at']


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model."""
    proforma_template = ProformaTemplateSerializer(read_only=True)
    proforma_template_id = serializers.UUIDField(write_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.UUIDField(write_only=True)
    completion_percent = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(source='item_statuses.count', read_only=True)
    verified_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'proforma_template', 'proforma_template_id', 'department', 'department_id',
            'start_date', 'due_date', 'status', 'completion_percent', 'items_count',
            'verified_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_completion_percent(self, obj):
        """Calculate completion percentage."""
        total = obj.item_statuses.count()
        if total == 0:
            return 0
        verified = obj.item_statuses.filter(status='Verified').count()
        return int((verified / total) * 100)
    
    def get_verified_count(self, obj):
        """Get count of verified items."""
        return obj.item_statuses.filter(status='Verified').count()


class AssignmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for assignment list view."""
    proforma_template_title = serializers.CharField(source='proforma_template.title', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    completion_percent = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'proforma_template_title', 'department_name', 'status',
            'start_date', 'due_date', 'completion_percent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_completion_percent(self, obj):
        """Calculate completion percentage."""
        total = obj.item_statuses.count()
        if total == 0:
            return 0
        verified = obj.item_statuses.filter(status='Verified').count()
        return int((verified / total) * 100)
