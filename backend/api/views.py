from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta
from .models import (
    Project, Indicator, Evidence, Section, Standard, IndicatorStatusHistory, 
    FrequencyLog, DigitalFormTemplate, EvidencePeriod, GoogleDriveFolderCache
)
from .serializers import (
    ProjectSerializer, IndicatorSerializer, EvidenceSerializer,
    SectionSerializer, StandardSerializer, CSVImportResultSerializer,
    UpcomingTaskSerializer, IndicatorStatusUpdateSerializer,
    IndicatorStatusHistorySerializer, FrequencyLogSerializer,
    DigitalFormTemplateSerializer, EvidencePeriodSerializer
)
from .csv_import_service import CSVImportService
from .scheduling_service import is_overdue, days_until_due, get_period_dates
from .google_drive_service import (
    initialize_project_drive_folder, ensure_indicator_folder_structure,
    upload_file_to_drive, get_file_share_link
)
from .compliance_service import (
    calculate_compliance_status, recalculate_indicator_compliance,
    get_missing_periods, update_evidence_period_compliance
)


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
    
    @action(detail=True, methods=['post'], url_path='link-google-drive')
    def link_google_drive(self, request, pk=None):
        """
        Link Google Drive to project via OAuth token.
        
        Expected input:
        {
            "oauth_token": {...}  # OAuth token JSON
        }
        """
        project = self.get_object()
        oauth_token = request.data.get('oauth_token')
        
        if not oauth_token:
            return Response(
                {'error': 'OAuth token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project.google_drive_oauth_token = oauth_token
        project.save(update_fields=['google_drive_oauth_token'])
        
        # Initialize folder structure
        folder_id = initialize_project_drive_folder(project)
        
        if folder_id:
            return Response({
                'message': 'Google Drive linked successfully',
                'folder_id': folder_id
            })
        else:
            return Response(
                {'error': 'Failed to initialize Google Drive folder'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='initialize-drive-folder')
    def initialize_drive_folder(self, request, pk=None):
        """Initialize Google Drive folder structure for project."""
        project = self.get_object()
        
        if not project.google_drive_oauth_token:
            return Response(
                {'error': 'Google Drive not linked. Please link Google Drive first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        folder_id = initialize_project_drive_folder(project)
        
        if folder_id:
            return Response({
                'message': 'Drive folder initialized',
                'folder_id': folder_id
            })
        else:
            return Response(
                {'error': 'Failed to initialize folder'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
    
    @action(detail=True, methods=['get'], url_path='compliance-status')
    def compliance_status(self, request, pk=None):
        """Get compliance status and missing periods for indicator."""
        indicator = self.get_object()
        status_data = calculate_compliance_status(indicator)
        return Response(status_data)
    
    @action(detail=True, methods=['get'], url_path='missing-periods')
    def missing_periods(self, request, pk=None):
        """Get missing evidence periods for indicator."""
        indicator = self.get_object()
        missing = get_missing_periods(indicator)
        return Response({'missing_periods': missing})
    
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
    
    Supports multiple evidence types:
    - File-based (Google Drive upload)
    - Text-only (physical evidence declarations)
    - Hybrid (text + optional file)
    - Form submissions
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
        """Handle evidence creation with Google Drive integration."""
        indicator = serializer.validated_data.get('indicator')
        evidence_type = serializer.validated_data.get('evidence_type', 'file')
        
        # Handle file upload to Google Drive
        if evidence_type in ['file', 'hybrid'] and 'file' in self.request.FILES:
            file_obj = self.request.FILES['file']
            
            # Ensure indicator folder structure exists
            folder_structure = ensure_indicator_folder_structure(indicator)
            if not folder_structure:
                raise ValidationError(
                    "Failed to create Google Drive folder structure. Please ensure Google Drive is linked."
                )
            
            # Determine upload folder based on file type
            uploads_folder_id = folder_structure.get('uploads')
            
            # Upload to Drive
            drive_result = upload_file_to_drive(
                file_obj, uploads_folder_id, indicator, file_obj.name
            )
            
            if drive_result:
                serializer.validated_data['google_drive_file_id'] = drive_result['file_id']
                serializer.validated_data['google_drive_file_name'] = drive_result['file_name']
                serializer.validated_data['google_drive_file_url'] = drive_result['file_url']
        
        # Save evidence
        evidence = serializer.save(uploaded_by=self.request.user)
        
        # Recalculate compliance
        recalculate_indicator_compliance(indicator)
        
        return evidence


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


class DigitalFormTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for DigitalFormTemplate CRUD operations."""
    queryset = DigitalFormTemplate.objects.all()
    serializer_class = DigitalFormTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter templates by indicator if indicator_id is provided."""
        queryset = DigitalFormTemplate.objects.all()
        indicator_id = self.request.query_params.get('indicator_id', None)
        if indicator_id is not None:
            queryset = queryset.filter(indicator_id=indicator_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)


class EvidencePeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for EvidencePeriod CRUD operations."""
    queryset = EvidencePeriod.objects.all()
    serializer_class = EvidencePeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter periods by indicator if indicator_id is provided."""
        queryset = EvidencePeriod.objects.all()
        indicator_id = self.request.query_params.get('indicator_id', None)
        if indicator_id is not None:
            queryset = queryset.filter(indicator_id=indicator_id)
        return queryset
    
    @action(detail=False, methods=['post'], url_path='recalculate')
    def recalculate(self, request):
        """Recalculate compliance for all evidence periods of an indicator."""
        indicator_id = request.data.get('indicator_id')
        if not indicator_id:
            return Response(
                {'error': 'indicator_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            indicator = Indicator.objects.get(pk=indicator_id)
            update_evidence_period_compliance(indicator)
            recalculate_indicator_compliance(indicator)
            return Response({'message': 'Compliance recalculated successfully'})
        except Indicator.DoesNotExist:
            return Response(
                {'error': 'Indicator not found'},
                status=status.HTTP_404_NOT_FOUND
            )
