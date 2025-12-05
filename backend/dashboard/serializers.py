"""
Serializers for dashboard app.
"""
from rest_framework import serializers
from assignments.serializers import AssignmentListSerializer


class AssignmentSummarySerializer(serializers.Serializer):
    """Serializer for assignment summary."""
    id = serializers.UUIDField()
    department_name = serializers.CharField()
    completion_percent = serializers.IntegerField()
    due_date = serializers.DateField()
    status = serializers.CharField()


class SectionSummarySerializer(serializers.Serializer):
    """Serializer for section summary."""
    code = serializers.CharField()
    title = serializers.CharField()
    completion_percent = serializers.IntegerField()


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary response."""
    overall_completion_percent = serializers.IntegerField()
    assignments = AssignmentSummarySerializer(many=True)
    sections = SectionSummarySerializer(many=True)


class PendingItemSerializer(serializers.Serializer):
    """Serializer for pending items."""
    id = serializers.UUIDField()
    assignment_id = serializers.UUIDField()
    assignment_title = serializers.CharField()
    department_name = serializers.CharField()
    item_code = serializers.CharField()
    item_text = serializers.CharField()
    section_code = serializers.CharField()
    status = serializers.CharField()
    due_date = serializers.DateField()
