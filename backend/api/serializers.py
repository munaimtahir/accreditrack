from rest_framework import serializers
from .models import Project, Indicator, Evidence


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    indicators_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'indicators_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_indicators_count(self, obj):
        return obj.indicators.count()


class EvidenceSerializer(serializers.ModelSerializer):
    """Serializer for Evidence model."""
    
    class Meta:
        model = Evidence
        fields = ['id', 'indicator', 'title', 'file', 'url', 'notes', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class IndicatorSerializer(serializers.ModelSerializer):
    """Serializer for Indicator model."""
    evidence = EvidenceSerializer(many=True, read_only=True)
    evidence_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Indicator
        fields = [
            'id', 'project', 'area', 'regulation_or_standard', 
            'requirement', 'evidence_required', 'responsible_person',
            'frequency', 'status', 'assigned_to', 'created_at', 
            'updated_at', 'evidence', 'evidence_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_evidence_count(self, obj):
        return obj.evidence.count()
