from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, Indicator, Evidence
from .serializers import ProjectSerializer, IndicatorSerializer, EvidenceSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations.
    
    Provides list, create, retrieve, update, and delete operations for Projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def indicators(self, request, pk=None):
        """Get all indicators for a specific project."""
        project = self.get_object()
        indicators = project.indicators.all()
        serializer = IndicatorSerializer(indicators, many=True)
        return Response(serializer.data)


class IndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Indicator CRUD operations.
    
    Provides list, create, retrieve, update, and delete operations for Indicators.
    """
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter indicators by project if project_id is provided."""
        queryset = Indicator.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    @action(detail=True, methods=['get'])
    def evidence_list(self, request, pk=None):
        """Get all evidence for a specific indicator."""
        indicator = self.get_object()
        evidence = indicator.evidence.all()
        serializer = EvidenceSerializer(evidence, many=True)
        return Response(serializer.data)


class EvidenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Evidence CRUD operations.
    
    Provides list, create, retrieve, update, and delete operations for Evidence.
    """
    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter evidence by indicator if indicator_id is provided."""
        queryset = Evidence.objects.all()
        indicator_id = self.request.query_params.get('indicator_id', None)
        if indicator_id is not None:
            queryset = queryset.filter(indicator_id=indicator_id)
        return queryset
