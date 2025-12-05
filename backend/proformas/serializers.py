"""
Serializers for proformas app.
"""
from rest_framework import serializers
from .models import ProformaTemplate, ProformaSection, ProformaItem


class ProformaItemSerializer(serializers.ModelSerializer):
    """Serializer for ProformaItem model."""
    
    class Meta:
        model = ProformaItem
        fields = ['id', 'code', 'requirement_text', 'required_evidence_type', 'importance_level', 'implementation_criteria', 'max_score', 'weightage_percent', 'is_licensing_critical', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProformaSectionSerializer(serializers.ModelSerializer):
    """Serializer for ProformaSection model."""
    items = ProformaItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    children = serializers.SerializerMethodField()
    parent_id = serializers.UUIDField(source='parent.id', read_only=True)
    parent_code = serializers.CharField(source='parent.code', read_only=True)
    
    class Meta:
        model = ProformaSection
        fields = ['id', 'code', 'title', 'weight', 'section_type', 'parent', 'parent_id', 'parent_code', 'items', 'items_count', 'children', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """Return child sections (standards) for categories."""
        if obj.section_type == 'CATEGORY':
            children = obj.children.all().order_by('weight', 'code')
            return ProformaSectionSerializer(children, many=True, context=self.context).data
        return []


class ProformaTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ProformaTemplate model."""
    sections = serializers.SerializerMethodField()
    sections_count = serializers.SerializerMethodField()
    module_code = serializers.CharField(source='module.code', read_only=True)
    module_display_name = serializers.CharField(source='module.display_name', read_only=True)
    
    class Meta:
        model = ProformaTemplate
        fields = ['id', 'code', 'title', 'authority_name', 'description', 'version', 'is_active', 'module', 'module_code', 'module_display_name', 'sections', 'sections_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sections(self, obj):
        """Return only category-level sections with their children."""
        categories = obj.sections.filter(section_type='CATEGORY', parent__isnull=True).order_by('weight', 'code')
        return ProformaSectionSerializer(categories, many=True, context=self.context).data
    
    def get_sections_count(self, obj):
        """Return count of all sections."""
        return obj.sections.count()


class ProformaTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template list view."""
    sections_count = serializers.IntegerField(source='sections.count', read_only=True)
    module_code = serializers.CharField(source='module.code', read_only=True)
    
    class Meta:
        model = ProformaTemplate
        fields = ['id', 'code', 'title', 'authority_name', 'version', 'is_active', 'module', 'module_code', 'sections_count', 'created_at']
        read_only_fields = ['id', 'created_at']
