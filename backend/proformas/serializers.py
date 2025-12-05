"""
Serializers for proformas app.
"""
from rest_framework import serializers
from .models import ProformaTemplate, ProformaSection, ProformaItem


class ProformaItemSerializer(serializers.ModelSerializer):
    """Serializer for ProformaItem model."""
    
    class Meta:
        model = ProformaItem
        fields = ['id', 'code', 'requirement_text', 'required_evidence_type', 'importance_level', 'implementation_criteria', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProformaSectionSerializer(serializers.ModelSerializer):
    """Serializer for ProformaSection model."""
    items = ProformaItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = ProformaSection
        fields = ['id', 'code', 'title', 'weight', 'items', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProformaTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ProformaTemplate model."""
    sections = ProformaSectionSerializer(many=True, read_only=True)
    sections_count = serializers.IntegerField(source='sections.count', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    module_display_name = serializers.CharField(source='module.display_name', read_only=True)
    
    class Meta:
        model = ProformaTemplate
        fields = ['id', 'title', 'authority_name', 'description', 'version', 'is_active', 'module', 'module_code', 'module_display_name', 'sections', 'sections_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProformaTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template list view."""
    sections_count = serializers.IntegerField(source='sections.count', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    
    class Meta:
        model = ProformaTemplate
        fields = ['id', 'title', 'authority_name', 'version', 'is_active', 'module', 'module_code', 'sections_count', 'created_at']
        read_only_fields = ['id', 'created_at']
