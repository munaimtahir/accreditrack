from rest_framework import serializers
from .models import (
    Project, Indicator, Evidence, Section, Standard, IndicatorStatusHistory, 
    FrequencyLog, DigitalFormTemplate, EvidencePeriod, GoogleDriveFolderCache
)


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section model."""
    standards_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'project', 'name', 'description', 'created_at', 'updated_at', 'standards_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_standards_count(self, obj):
        return obj.standards.count()


class StandardSerializer(serializers.ModelSerializer):
    """Serializer for Standard model."""
    indicators_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Standard
        fields = ['id', 'section', 'name', 'description', 'created_at', 'updated_at', 'indicators_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_indicators_count(self, obj):
        return obj.indicators.count()


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializes Project model instances.

    Includes a calculated field for the number of associated indicators.
    """
    indicators_count = serializers.SerializerMethodField()
    sections_count = serializers.SerializerMethodField()
    google_drive_linked = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'created_at', 'updated_at', 
            'indicators_count', 'sections_count',
            'google_drive_root_folder_id', 'google_drive_linked_at', 'google_drive_linked'
        ]
        read_only_fields = ['created_at', 'updated_at', 'google_drive_linked']
        extra_kwargs = {
            'google_drive_oauth_token': {'write_only': True}  # Don't expose tokens in responses
        }
    
    def get_indicators_count(self, obj):
        """
        Calculates the number of indicators associated with the project.

        Args:
            obj (Project): The project instance.

        Returns:
            int: The count of indicators for the project.
        """
        return obj.indicators.count()
    
    def get_sections_count(self, obj):
        return obj.sections.count()
    
    def get_google_drive_linked(self, obj):
        return bool(obj.google_drive_root_folder_id)


class EvidenceSerializer(serializers.ModelSerializer):
    """
    Serializes Evidence model instances.
    """
    
    class Meta:
        model = Evidence
        fields = [
            'id', 'indicator', 'title', 'evidence_type', 'evidence_type_display',
            'google_drive_file_id', 'google_drive_file_name', 'google_drive_file_url',
            'evidence_text', 'period_start', 'period_end',
            'form_data', 'form_template',
            'file', 'url',  # Legacy fields
            'notes', 'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at', 'uploaded_by_name', 'evidence_type_display']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.username
        return None
    
    def validate(self, data):
        """Validate evidence based on evidence_type and indicator evidence_mode."""
        indicator = data.get('indicator')
        evidence_type = data.get('evidence_type', 'file')
        
        if indicator:
            evidence_mode = indicator.evidence_mode
            
            # Validate based on indicator's evidence_mode
            if evidence_mode == 'file_only':
                if evidence_type not in ['file', 'hybrid']:
                    raise serializers.ValidationError(
                        "This indicator requires file-based evidence."
                    )
                if not data.get('google_drive_file_id') and not data.get('file'):
                    raise serializers.ValidationError(
                        "File is required for this indicator."
                    )
            
            elif evidence_mode == 'text_only':
                if not data.get('evidence_text'):
                    raise serializers.ValidationError(
                        "Text declaration is required for this indicator."
                    )
            
            elif evidence_mode == 'frequency_log':
                if not data.get('period_start') or not data.get('period_end'):
                    raise serializers.ValidationError(
                        "Period start and end dates are required for frequency-based evidence."
                    )
        
        return data


class IndicatorSerializer(serializers.ModelSerializer):
    """
    Serializes Indicator model instances.

    Includes nested serialization of related evidence and a count of evidence items.
    """
    evidence = EvidenceSerializer(many=True, read_only=True)
    evidence_count = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()
    standard_name = serializers.SerializerMethodField()
    assigned_user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Indicator
        fields = [
            'id', 'project', 'section', 'section_name', 'standard', 'standard_name',
            'area', 'regulation_or_standard', 
            'requirement', 'evidence_required', 'responsible_person',
            'frequency', 'normalized_frequency', 'schedule_type', 'next_due_date', 'is_active',
            'evidence_mode', 'indicator_code',
            'status', 'score', 'compliance_notes',
            'assigned_to', 'assigned_user', 'assigned_user_name',
            'indicator_key', 'ai_confidence_score',
            'created_at', 'updated_at', 'evidence', 'evidence_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'indicator_key']
    
    def get_evidence_count(self, obj):
        """
        Calculates the number of evidence items associated with the indicator.

        Args:
            obj (Indicator): The indicator instance.

        Returns:
            int: The count of evidence for the indicator.
        """
        return obj.evidence.count()
    
    def get_section_name(self, obj):
        return obj.section.name if obj.section else obj.area
    
    def get_standard_name(self, obj):
        return obj.standard.name if obj.standard else obj.regulation_or_standard
    
    def get_assigned_user_name(self, obj):
        if obj.assigned_user:
            return obj.assigned_user.username
        return obj.assigned_to


class CSVImportResultSerializer(serializers.Serializer):
    """Serializer for CSV import results."""
    sections_created = serializers.IntegerField()
    standards_created = serializers.IntegerField()
    indicators_created = serializers.IntegerField()
    indicators_updated = serializers.IntegerField()
    rows_skipped = serializers.IntegerField()
    total_rows_processed = serializers.IntegerField()
    errors = serializers.ListField()
    unmatched_users = serializers.ListField()


class UpcomingTaskSerializer(serializers.Serializer):
    """Serializer for upcoming tasks."""
    indicator_id = serializers.IntegerField()
    requirement = serializers.CharField()
    section = serializers.CharField()
    standard = serializers.CharField()
    due_date = serializers.DateField()
    is_overdue = serializers.BooleanField()
    days_until_due = serializers.IntegerField()
    assigned_to = serializers.CharField()
    status = serializers.CharField()
    schedule_type = serializers.CharField()
    frequency = serializers.CharField()


class IndicatorStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating indicator status."""
    status = serializers.ChoiceField(choices=Indicator.STATUS_CHOICES)
    score = serializers.IntegerField(required=False, min_value=0, max_value=100)
    notes = serializers.CharField(required=False, allow_blank=True)


class IndicatorStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for IndicatorStatusHistory model."""
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = IndicatorStatusHistory
        fields = ['id', 'indicator', 'old_status', 'new_status', 'changed_by', 'changed_by_name', 'notes', 'timestamp']
        read_only_fields = ['timestamp']
    
    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.username
        return None


class FrequencyLogSerializer(serializers.ModelSerializer):
    """Serializer for FrequencyLog model."""
    submitted_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FrequencyLog
        fields = ['id', 'indicator', 'period_start', 'period_end', 'submitted_at', 'submitted_by', 'submitted_by_name', 'notes', 'is_compliant']
        read_only_fields = ['submitted_at']
    
    def get_submitted_by_name(self, obj):
        if obj.submitted_by:
            return obj.submitted_by.username
        return None


class DigitalFormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for DigitalFormTemplate model."""
    created_by_name = serializers.SerializerMethodField()
    indicator_requirement = serializers.SerializerMethodField()
    
    class Meta:
        model = DigitalFormTemplate
        fields = [
            'id', 'indicator', 'indicator_requirement', 'name', 'description', 
            'form_fields', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by_name', 'indicator_requirement']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return None
    
    def get_indicator_requirement(self, obj):
        return obj.indicator.requirement[:100] if obj.indicator else None


class EvidencePeriodSerializer(serializers.ModelSerializer):
    """Serializer for EvidencePeriod model."""
    indicator_requirement = serializers.SerializerMethodField()
    compliance_status = serializers.SerializerMethodField()
    
    class Meta:
        model = EvidencePeriod
        fields = [
            'id', 'indicator', 'indicator_requirement', 'period_start', 'period_end',
            'expected_evidence_count', 'actual_evidence_count', 'is_compliant',
            'compliance_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'indicator_requirement', 'compliance_status']
    
    def get_indicator_requirement(self, obj):
        return obj.indicator.requirement[:100] if obj.indicator else None
    
    def get_compliance_status(self, obj):
        if obj.is_compliant:
            return 'compliant'
        elif obj.actual_evidence_count > 0:
            return 'in_process'
        else:
            return 'not_compliant'
