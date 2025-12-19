from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta
from .models import Project, Indicator, Evidence, Section, Standard, IndicatorStatusHistory, FrequencyLog
from .serializers import (
    ProjectSerializer, IndicatorSerializer, EvidenceSerializer,
    SectionSerializer, StandardSerializer, CSVImportResultSerializer,
    UpcomingTaskSerializer, IndicatorStatusUpdateSerializer,
    IndicatorStatusHistorySerializer, FrequencyLogSerializer
)
from .csv_import_service import CSVImportService
from .scheduling_service import is_overdue, days_until_due, get_period_dates


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
    
    @action(detail=True, methods=['post'], url_path='indicators/import-csv')
    def import_csv(self, request, pk=None):
        """
        Import indicators from CSV file.
        
        Expected CSV format:
        Section, Standard, Indicator, Evidence Required, Responsible Person,
        Frequency, Assigned to, Compliance Evidence, Score
        """
        project = self.get_object()
        
        # Check if file is provided
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided. Please upload a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        # Validate file extension
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Invalid file format. Please upload a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import CSV
        import_service = CSVImportService(project)
        result = import_service.import_csv(csv_file)
        
        # Serialize and return results
        serializer = CSVImportResultSerializer(result.to_dict())
        
        # Return 400 if there were errors, 200 otherwise
        if result.errors and result.indicators_created == 0 and result.indicators_updated == 0:
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='upcoming-tasks')
    def upcoming_tasks(self, request, pk=None):
        """
        Get upcoming compliance tasks for a project.
        
        Returns tasks sorted by:
        1. Overdue items first
        2. Then by nearest due date
        
        Query parameters:
        - days_ahead: Number of days to look ahead (default: 30)
        """
        project = self.get_object()
        days_ahead = int(request.query_params.get('days_ahead', 30))
        
        today = date.today()
        future_date = today + timedelta(days=days_ahead)
        
        tasks = []
        
        # Get all active indicators for the project
        indicators = project.indicators.filter(is_active=True)
        
        for indicator in indicators:
            # One-time indicators: appear until marked compliant
            if indicator.schedule_type == 'one_time':
                if indicator.status != 'compliant':
                    # Use next_due_date if set, otherwise use created_at as due date
                    due_date = indicator.next_due_date or indicator.created_at.date()
                    
                    tasks.append({
                        'indicator_id': indicator.id,
                        'requirement': indicator.requirement,
                        'section': indicator.section.name if indicator.section else indicator.area,
                        'standard': indicator.standard.name if indicator.standard else indicator.regulation_or_standard,
                        'due_date': due_date,
                        'is_overdue': is_overdue(due_date, today),
                        'days_until_due': days_until_due(due_date, today),
                        'assigned_to': indicator.assigned_user.username if indicator.assigned_user else indicator.assigned_to,
                        'status': indicator.status,
                        'schedule_type': indicator.schedule_type,
                        'frequency': indicator.normalized_frequency or indicator.frequency,
                    })
            
            # Recurring indicators: appear when due date is approaching or overdue
            elif indicator.schedule_type == 'recurring':
                if indicator.next_due_date:
                    due_date = indicator.next_due_date
                    
                    # Include if overdue or within the future window
                    if due_date <= future_date:
                        # Check if there's a log for the current period
                        period_start, period_end = get_period_dates(
                            indicator.normalized_frequency or indicator.frequency,
                            today
                        )
                        
                        # Check if compliance log exists for current period
                        has_current_log = FrequencyLog.objects.filter(
                            indicator=indicator,
                            period_start=period_start,
                            period_end=period_end,
                            is_compliant=True
                        ).exists()
                        
                        # Only show task if no compliant log for current period
                        if not has_current_log:
                            tasks.append({
                                'indicator_id': indicator.id,
                                'requirement': indicator.requirement,
                                'section': indicator.section.name if indicator.section else indicator.area,
                                'standard': indicator.standard.name if indicator.standard else indicator.regulation_or_standard,
                                'due_date': due_date,
                                'is_overdue': is_overdue(due_date, today),
                                'days_until_due': days_until_due(due_date, today),
                                'assigned_to': indicator.assigned_user.username if indicator.assigned_user else indicator.assigned_to,
                                'status': indicator.status,
                                'schedule_type': indicator.schedule_type,
                                'frequency': indicator.normalized_frequency or indicator.frequency,
                            })
        
        # Sort tasks: overdue first, then by due date
        tasks.sort(key=lambda x: (not x['is_overdue'], x['due_date']))
        
        serializer = UpcomingTaskSerializer(tasks, many=True)
        return Response(serializer.data)


class SectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Section CRUD operations."""
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter sections by project if project_id is provided."""
        queryset = Section.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class StandardViewSet(viewsets.ModelViewSet):
    """ViewSet for Standard CRUD operations."""
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter standards by section if section_id is provided."""
        queryset = Standard.objects.all()
        section_id = self.request.query_params.get('section_id', None)
        if section_id is not None:
            queryset = queryset.filter(section_id=section_id)
        return queryset


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
    
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Update indicator status and optionally score.
        
        Expected input:
        {
            "status": "compliant",
            "score": 10,
            "notes": "Optional notes"
        }
        """
        indicator = self.get_object()
        serializer = IndicatorStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = indicator.status
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        # Update indicator
        indicator.status = new_status
        if 'score' in serializer.validated_data:
            indicator.score = serializer.validated_data['score']
        indicator.save()
        
        # Create status history entry
        IndicatorStatusHistory.objects.create(
            indicator=indicator,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            notes=notes
        )
        
        return Response(IndicatorSerializer(indicator).data)


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
    
    def perform_create(self, serializer):
        """Set uploaded_by to current user."""
        serializer.save(uploaded_by=self.request.user)


class FrequencyLogViewSet(viewsets.ModelViewSet):
    """ViewSet for FrequencyLog CRUD operations."""
    queryset = FrequencyLog.objects.all()
    serializer_class = FrequencyLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter logs by indicator if indicator_id is provided."""
        queryset = FrequencyLog.objects.all()
        indicator_id = self.request.query_params.get('indicator_id', None)
        if indicator_id is not None:
            queryset = queryset.filter(indicator_id=indicator_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set submitted_by to current user."""
        serializer.save(submitted_by=self.request.user)
