from rest_framework import serializers
from .models import Project, Indicator, Evidence


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializes Project model instances.

    Includes a calculated field for the number of associated indicators.
    """
    indicators_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'indicators_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_indicators_count(self, obj):
        """
        Calculates the number of indicators associated with the project.

        Args:
            obj (Project): The project instance.

        Returns:
            int: The count of indicators for the project.
        """
        return obj.indicators.count()


class EvidenceSerializer(serializers.ModelSerializer):
    """
    Serializes Evidence model instances.
    """
    
    class Meta:
        model = Evidence
        fields = ['id', 'indicator', 'title', 'file', 'url', 'notes', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class IndicatorSerializer(serializers.ModelSerializer):
    """
    Serializes Indicator model instances.

    Includes nested serialization of related evidence and a count of evidence items.
    """
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
        """
        Calculates the number of evidence items associated with the indicator.

        Args:
            obj (Indicator): The indicator instance.

        Returns:
            int: The count of evidence for the indicator.
        """
        return obj.evidence.count()
