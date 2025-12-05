"""
Views for assignments app.
"""
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Assignment, ItemStatus
from .serializers import AssignmentSerializer, AssignmentListSerializer, ItemStatusSerializer
from accounts.permissions import IsQAAdmin, IsDepartmentCoordinator
from proformas.models import ProformaItem


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Assignment CRUD operations."""
    queryset = Assignment.objects.select_related('proforma_template', 'department').prefetch_related('item_statuses').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return AssignmentListSerializer
        return AssignmentSerializer
    
    def get_permissions(self):
        """Override permissions based on action."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsQAAdmin()]
    
    def get_queryset(self):
        """Filter queryset based on user role and query parameters."""
        queryset = super().get_queryset()
        
        # QAAdmin and SuperAdmin see all assignments
        if self.request.user.is_superuser or self.request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists():
            pass  # No filtering needed
        else:
            # DepartmentCoordinator sees only their department's assignments
            user_departments = self.request.user.user_roles.filter(
                role__name='DepartmentCoordinator'
            ).values_list('department_id', flat=True)
            
            if user_departments:
                queryset = queryset.filter(department_id__in=user_departments)
            else:
                # Viewer sees all (read-only)
                pass
        
        # Apply filters
        template_id = self.request.query_params.get('template')
        if template_id:
            queryset = queryset.filter(proforma_template_id=template_id)
        
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        due_before = self.request.query_params.get('due_before')
        if due_before:
            queryset = queryset.filter(due_date__lte=due_before)
        
        due_after = self.request.query_params.get('due_after')
        if due_after:
            queryset = queryset.filter(due_date__gte=due_after)
        
        return queryset
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create assignment(s) and auto-create ItemStatus records."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Handle multiple departments
        departments = request.data.get('departments', [])
        if not departments:
            # Single department
            departments = [request.data.get('department_id')]
        
        template_id = request.data.get('proforma_template_id')
        template = serializer.validated_data.get('proforma_template_id')
        if isinstance(template, str):
            from proformas.models import ProformaTemplate
            template = ProformaTemplate.objects.get(id=template)
        elif hasattr(template, 'id'):
            template = template
        
        # Get all items from the template
        items = ProformaItem.objects.filter(
            section__template_id=template_id
        ).select_related('section')
        
        created_assignments = []
        for dept_id in departments:
            assignment = Assignment.objects.create(
                proforma_template_id=template_id,
                department_id=dept_id,
                start_date=serializer.validated_data['start_date'],
                due_date=serializer.validated_data['due_date'],
                status=serializer.validated_data.get('status', 'NotStarted')
            )
            
            # Auto-create ItemStatus for each item
            item_statuses = [
                ItemStatus(
                    assignment=assignment,
                    proforma_item=item,
                    status='NotStarted',
                    completion_percent=0
                )
                for item in items
            ]
            ItemStatus.objects.bulk_create(item_statuses)
            
            created_assignments.append(assignment)
        
        # Return the first assignment if single, or list if multiple
        if len(created_assignments) == 1:
            serializer = self.get_serializer(created_assignments[0])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            serializer = self.get_serializer(created_assignments, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='items')
    def items(self, request, pk=None):
        """Get all items with status for this assignment."""
        assignment = self.get_object()
        item_statuses = assignment.item_statuses.select_related(
            'proforma_item__section'
        ).order_by('proforma_item__section__weight', 'proforma_item__code')
        
        # Group by section
        sections_data = {}
        for item_status in item_statuses:
            section = item_status.proforma_item.section
            if section.id not in sections_data:
                sections_data[section.id] = {
                    'section': {
                        'id': str(section.id),
                        'code': section.code,
                        'title': section.title,
                        'weight': section.weight,
                    },
                    'items': []
                }
            
            serializer = ItemStatusSerializer(item_status)
            sections_data[section.id]['items'].append(serializer.data)
        
        return Response(list(sections_data.values()))


class ItemStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for ItemStatus operations."""
    queryset = ItemStatus.objects.select_related('assignment', 'proforma_item', 'last_updated_by').all()
    serializer_class = ItemStatusSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']  # Only allow GET and PATCH
    
    def get_permissions(self):
        """Override permissions - coordinators and QAAdmins can update."""
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return [IsAuthenticated()]  # Will check in partial_update
    
    def partial_update(self, request, *args, **kwargs):
        """Update item status with permission checks."""
        item_status = self.get_object()
        assignment = item_status.assignment
        
        # Check permissions
        is_qa_admin = request.user.is_superuser or request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()
        
        is_coordinator = request.user.user_roles.filter(
            role__name='DepartmentCoordinator',
            department=assignment.department
        ).exists()
        
        if not (is_qa_admin or is_coordinator):
            return Response(
                {'detail': 'You do not have permission to update this item status.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate status transitions
        new_status = request.data.get('status')
        if new_status:
            current_status = item_status.status
            
            # Coordinators can: NotStarted -> InProgress -> Submitted
            if is_coordinator and not is_qa_admin:
                valid_transitions = {
                    'NotStarted': ['InProgress'],
                    'InProgress': ['Submitted', 'NotStarted'],
                    'Submitted': ['InProgress'],
                }
                if current_status in valid_transitions:
                    if new_status not in valid_transitions[current_status]:
                        return Response(
                            {'detail': f'Invalid status transition from {current_status} to {new_status}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            # QAAdmins can mark as Verified/Rejected
            if is_qa_admin and new_status in ['Verified', 'Rejected']:
                if current_status != 'Submitted':
                    return Response(
                        {'detail': 'Can only verify/reject items that are Submitted'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Update the item status
        serializer = self.get_serializer(item_status, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Set last_updated_by
        item_status.last_updated_by = request.user
        serializer.save(last_updated_by=request.user)
        
        return Response(serializer.data)
