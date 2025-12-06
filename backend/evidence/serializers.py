"""
Serializers for evidence app.
"""
from rest_framework import serializers
from .models import Evidence


class EvidenceSerializer(serializers.ModelSerializer):
    """Serializer for Evidence model."""
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = Evidence
        fields = [
            'id', 'item_status', 'file', 'file_url', 'file_name', 'file_size',
            'description', 'note', 'reference_code', 'evidence_type', 'uploaded_by', 'uploaded_by_email', 'uploaded_at', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'created_at']
    
    def get_file_url(self, obj):
        """Get file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_name(self, obj):
        """Get file name."""
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None
    
    def get_file_size(self, obj):
        """Get file size in bytes."""
        if obj.file:
            try:
                return obj.file.size
            except (OSError, ValueError):
                return None
        return None
