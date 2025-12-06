"""
Views for assignments app.
"""
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Assignment, ItemStatus, AssignmentUpdate
from .serializers import AssignmentSerializer, AssignmentListSerializer, ItemStatusSerializer, AssignmentUpdateSerializer
from .services import update_assignment_status, auto_update_assignment_status
from accounts.permissions import IsQAAdmin, IsDepartmentCoordinator
from proformas.models import ProformaItem


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Assignment CRUD operations."""
    queryset = Assignment.objects.select_related(
        'proforma_template', 'department', 'section', 'proforma_item'
    ).prefetch_related('item_statuses', 'assigned_to').all()
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
                # Users see their own assignments
                queryset = queryset.filter(assigned_to=self.request.user)
        
        # Apply filters
        template_id = self.request.query_params.get('template')
        if template_id:
            queryset = queryset.filter(proforma_template_id=template_id)
        
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(assigned_to__id=user_id)
        
        scope_type = self.request.query_params.get('scope_type')
        if scope_type:
            queryset = queryset.filter(scope_type=scope_type)
        
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
        
        template_id = request.data.get('proforma_template_id')
        department_id = request.data.get('department_id')
        assigned_to_user_ids = request.data.get('assigned_to', [])
        scope_type = request.data.get('scope_type', 'DEPARTMENT')
        section_id = request.data.get('section')
        proforma_item_id = request.data.get('proforma_item')
        instructions = request.data.get('instructions', '')
        
        # Determine which items to create ItemStatus for
        if scope_type == 'INDICATOR' and proforma_item_id:
            # Single item assignment
            items = ProformaItem.objects.filter(id=proforma_item_id)
        elif scope_type == 'SECTION' and section_id:
            # Section assignment
            items = ProformaItem.objects.filter(section_id=section_id)
        else:
            # Department assignment - all items from template
            items = ProformaItem.objects.filter(
                section__template_id=template_id
            ).select_related('section')
        
        # Handle multiple departments or users
        departments = request.data.get('departments', [])
        if not departments and department_id:
            departments = [department_id]
        
        created_assignments = []
        
        # If user assignments, create one per user
        if assigned_to_user_ids:
            for user_id in assigned_to_user_ids:
                assignment = Assignment.objects.create(
                    proforma_template_id=template_id,
                    department_id=department_id,
                    scope_type=scope_type,
                    section_id=section_id,
                    proforma_item_id=proforma_item_id,
                    instructions=instructions,
                    start_date=serializer.validated_data['start_date'],
                    due_date=serializer.validated_data['due_date'],
                    status=serializer.validated_data.get('status', 'NOT_STARTED')
                )
                assignment.assigned_to.add(user_id)
                
                # Auto-create ItemStatus for relevant items
                item_statuses = [
                    ItemStatus(
                        assignment=assignment,
                        proforma_item=item,
                        status='NOT_STARTED',
                        completion_percent=0
                    )
                    for item in items
                ]
                ItemStatus.objects.bulk_create(item_statuses)
                
                created_assignments.append(assignment)
        else:
            # Department-based assignments
            for dept_id in departments:
                assignment = Assignment.objects.create(
                    proforma_template_id=template_id,
                    department_id=dept_id,
                    scope_type=scope_type,
                    section_id=section_id,
                    proforma_item_id=proforma_item_id,
                    instructions=instructions,
                    start_date=serializer.validated_data['start_date'],
                    due_date=serializer.validated_data['due_date'],
                    status=serializer.validated_data.get('status', 'NOT_STARTED')
                )
                
                # Auto-create ItemStatus for relevant items
                item_statuses = [
                    ItemStatus(
                        assignment=assignment,
                        proforma_item=item,
                        status='NOT_STARTED',
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
    
    @action(detail=True, methods=['post'], url_path='submit-for-review')
    def submit_for_review(self, request, pk=None):
        """Submit assignment for review (coordinator action)."""
        assignment = self.get_object()
        
        # Check permissions
        is_coordinator = request.user.user_roles.filter(
            role__name='DepartmentCoordinator',
            department=assignment.department
        ).exists()
        
        if not is_coordinator:
            return Response(
                {'detail': 'Only department coordinators can submit assignments for review.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        note = request.data.get('note', 'Assignment submitted for review')
        update_assignment_status(assignment, 'PENDING_REVIEW', request.user, note)
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """Verify assignment (QA admin action)."""
        assignment = self.get_object()
        
        # Check permissions
        is_qa_admin = request.user.is_superuser or request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()
        
        if not is_qa_admin:
            return Response(
                {'detail': 'Only QA admins can verify assignments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        note = request.data.get('note', 'Assignment verified')
        update_assignment_status(assignment, 'VERIFIED', request.user, note)
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='updates')
    def updates(self, request, pk=None):
        """Get progress log timeline for this assignment."""
        assignment = self.get_object()
        updates = assignment.updates.select_related('user').order_by('-created_at')
        serializer = AssignmentUpdateSerializer(updates, many=True)
        return Response(serializer.data)


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
            
            # Coordinators can: NOT_STARTED -> IN_PROGRESS -> PENDING_REVIEW
            if is_coordinator and not is_qa_admin:
                valid_transitions = {
                    'NOT_STARTED': ['IN_PROGRESS'],
                    'IN_PROGRESS': ['PENDING_REVIEW', 'NOT_STARTED'],
                    'PENDING_REVIEW': ['IN_PROGRESS'],
                }
                if current_status in valid_transitions:
                    if new_status not in valid_transitions[current_status]:
                        return Response(
                            {'detail': f'Invalid status transition from {current_status} to {new_status}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            # QAAdmins can mark as VERIFIED/REJECTED
            if is_qa_admin and new_status in ['VERIFIED', 'REJECTED']:
                if current_status != 'PENDING_REVIEW':
                    return Response(
                        {'detail': 'Can only verify/reject items that are PENDING_REVIEW'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Update the item status
        serializer = self.get_serializer(item_status, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Set last_updated_by
        item_status.last_updated_by = request.user
        serializer.save(last_updated_by=request.user)
        
        # Auto-update assignment status
        auto_update_assignment_status(item_status.assignment)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='submit-for-review')
    def submit_for_review(self, request, pk=None):
        """Submit item status for review (coordinator action)."""
        item_status = self.get_object()
        assignment = item_status.assignment
        
        # Check permissions
        is_coordinator = request.user.user_roles.filter(
            role__name='DepartmentCoordinator',
            department=assignment.department
        ).exists()
        
        if not is_coordinator:
            return Response(
                {'detail': 'Only department coordinators can submit for review.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if item_status.status not in ['IN_PROGRESS', 'NOT_STARTED']:
            return Response(
                {'detail': f'Cannot submit item with status {item_status.status} for review.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item_status.status = 'PENDING_REVIEW'
        item_status.last_updated_by = request.user
        item_status.save()
        
        # Auto-update assignment status
        auto_update_assignment_status(assignment)
        
        serializer = self.get_serializer(item_status)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """Verify item status (QA admin action)."""
        item_status = self.get_object()
        assignment = item_status.assignment
        
        # Check permissions
        is_qa_admin = request.user.is_superuser or request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()
        
        if not is_qa_admin:
            return Response(
                {'detail': 'Only QA admins can verify items.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if item_status.status != 'PENDING_REVIEW':
            return Response(
                {'detail': 'Can only verify items that are pending review.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item_status.status = 'VERIFIED'
        item_status.completion_percent = 100
        item_status.last_updated_by = request.user
        item_status.save()
        
        # Auto-update assignment status
        auto_update_assignment_status(assignment)
        
        serializer = self.get_serializer(item_status)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='mark-in-progress')
    def mark_in_progress(self, request, pk=None):
        """Mark item status as in progress."""
        item_status = self.get_object()
        assignment = item_status.assignment
        
        # Check permissions
        is_coordinator = request.user.user_roles.filter(
            role__name='DepartmentCoordinator',
            department=assignment.department
        ).exists()
        
        is_qa_admin = request.user.is_superuser or request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()
        
        if not (is_coordinator or is_qa_admin):
            return Response(
                {'detail': 'You do not have permission to update this item.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        item_status.status = 'IN_PROGRESS'
        item_status.last_updated_by = request.user
        item_status.save()
        
        # Auto-update assignment status
        auto_update_assignment_status(assignment)
        
        serializer = self.get_serializer(item_status)
        return Response(serializer.data)


class AssignmentUpdateViewSet(viewsets.ModelViewSet):
    """ViewSet for AssignmentUpdate operations."""
    queryset = AssignmentUpdate.objects.select_related('assignment', 'user').all()
    serializer_class = AssignmentUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']  # Only allow GET and POST
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        assignment_id = self.request.query_params.get('assignment')
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Users can only see updates for their own assignments or if they're admins
        if not (self.request.user.is_superuser or self.request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()):
            # Filter to show only updates for assignments assigned to the user
            user_assignment_ids = Assignment.objects.filter(
                assigned_to=self.request.user
            ).values_list('id', flat=True)
            queryset = queryset.filter(assignment_id__in=user_assignment_ids)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the user to the current user."""
        serializer.save(user=self.request.user)
