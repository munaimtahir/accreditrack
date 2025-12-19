from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, Indicator, Evidence
from .serializers import ProjectSerializer, IndicatorSerializer, EvidenceSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations for Projects.

    Provides the following actions:
    - list: Retrieve a list of all projects.
    - create: Create a new project instance.
    - retrieve: Retrieve a specific project instance.
    - update: Update a specific project instance.
    - partial_update: Partially update a specific project instance.
    - destroy: Delete a specific project instance.
    - indicators: Retrieve all indicators for a specific project.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def indicators(self, request, pk=None):
        """
        Retrieves all indicators associated with a specific project.

        Args:
            request (Request): The request object.
            pk (int, optional): The primary key of the project. Defaults to None.

        Returns:
            Response: A response containing the serialized data of the indicators.
        """
        project = self.get_object()
        indicators = project.indicators.all()
        serializer = IndicatorSerializer(indicators, many=True)
        return Response(serializer.data)


class IndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations for Indicators.

    Provides standard CRUD actions and allows filtering by `project_id`.
    """
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filters the queryset to indicators belonging to a specific project.

        The project is specified by the `project_id` query parameter.

        Returns:
            QuerySet: A queryset of indicators.
        """
        queryset = Indicator.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    @action(detail=True, methods=['get'])
    def evidence_list(self, request, pk=None):
        """
        Retrieves all evidence associated with a specific indicator.

        Args:
            request (Request): The request object.
            pk (int, optional): The primary key of the indicator. Defaults to None.

        Returns:
            Response: A response containing the serialized data of the evidence.
        """
        indicator = self.get_object()
        evidence = indicator.evidence.all()
        serializer = EvidenceSerializer(evidence, many=True)
        return Response(serializer.data)


class EvidenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations for Evidence.

    Provides standard CRUD actions and allows filtering by `indicator_id`.
    """
    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filters the queryset to evidence belonging to a specific indicator.

        The indicator is specified by the `indicator_id` query parameter.

        Returns:
            QuerySet: A queryset of evidence.
        """
        queryset = Evidence.objects.all()
        indicator_id = self.request.query_params.get('indicator_id', None)
        if indicator_id is not None:
            queryset = queryset.filter(indicator_id=indicator_id)
        return queryset
