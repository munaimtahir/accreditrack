"""
Views for dashboard app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from assignments.models import Assignment, ItemStatus
from proformas.models import ProformaTemplate
from .services import (
    calculate_assignment_completion,
    get_section_summaries,
    get_pending_items,
    get_module_stats,
    get_module_category_breakdown,
    get_user_assignments,
    get_template_stats
)
from .serializers import DashboardSummarySerializer, PendingItemSerializer
from modules.models import Module, UserModuleRole


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Get dashboard summary with optional filters."""
    template_id = request.query_params.get('template')
    department_id = request.query_params.get('department')
    
    # Get assignments based on filters and user role
    assignments = Assignment.objects.select_related(
        'proforma_template', 'department'
    ).prefetch_related('item_statuses').all()
    
    # Apply role-based filtering
    is_qa_admin = request.user.is_superuser or request.user.user_roles.filter(
        role__name__in=['SuperAdmin', 'QAAdmin']
    ).exists()
    
    if not is_qa_admin:
        # DepartmentCoordinator sees only their department's assignments
        user_departments = request.user.user_roles.filter(
            role__name='DepartmentCoordinator'
        ).values_list('department_id', flat=True)
        
        if user_departments:
            assignments = assignments.filter(department_id__in=user_departments)
    
    # Apply filters
    if template_id:
        assignments = assignments.filter(proforma_template_id=template_id)
    
    if department_id:
        assignments = assignments.filter(department_id=department_id)
    
    # Calculate overall completion
    if assignments.exists():
        all_item_statuses = ItemStatus.objects.filter(
            assignment__in=assignments
        )
        total = all_item_statuses.count()
        verified = all_item_statuses.filter(status='VERIFIED').count()
        overall_completion = int((verified / total) * 100) if total > 0 else 0
    else:
        overall_completion = 0
    
    # Get assignment summaries
    assignment_summaries = []
    for assignment in assignments:
        completion = calculate_assignment_completion(assignment)
        assignment_summaries.append({
            'id': str(assignment.id),
            'department_name': assignment.department.name,
            'completion_percent': completion,
            'due_date': assignment.due_date,
            'status': assignment.status,
        })
    
    # Get section summaries (if template is specified)
    section_summaries = []
    if template_id:
        try:
            template = ProformaTemplate.objects.get(id=template_id)
            # Use first assignment for section calculation if available
            if assignments.exists():
                first_assignment = assignments.first()
                section_summaries = get_section_summaries(first_assignment)
                section_summaries = [
                    {
                        'code': s['section']['code'],
                        'title': s['section']['title'],
                        'completion_percent': s['completion_percent'],
                    }
                    for s in section_summaries
                ]
        except ProformaTemplate.DoesNotExist:
            pass
    
    response_data = {
        'overall_completion_percent': overall_completion,
        'assignments': assignment_summaries,
        'sections': section_summaries,
    }
    
    serializer = DashboardSummarySerializer(data=response_data)
    serializer.is_valid()
    return Response(serializer.validated_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_items(request):
    """Get list of pending items."""
    template_id = request.query_params.get('template')
    department_id = request.query_params.get('department')
    
    pending = get_pending_items(
        request.user,
        template_id=template_id,
        department_id=department_id
    )
    
    items_data = []
    for item_status in pending[:100]:  # Limit to 100 items
        items_data.append({
            'id': str(item_status.id),
            'assignment_id': str(item_status.assignment.id),
            'assignment_title': item_status.assignment.proforma_template.title,
            'department_name': item_status.assignment.department.name,
            'item_code': item_status.proforma_item.code,
            'item_text': item_status.proforma_item.requirement_text[:100],  # Truncate
            'section_code': item_status.proforma_item.section.code,
            'status': item_status.status,
            'due_date': item_status.assignment.due_date,
        })
    
    serializer = PendingItemSerializer(data=items_data, many=True)
    serializer.is_valid()
    return Response(serializer.validated_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def modules_list(request):
    """List all modules with stats (for SUPERADMIN)."""
    # Check if user is super admin
    is_super_admin = request.user.is_superuser or request.user.user_roles.filter(
        role__name='SuperAdmin'
    ).exists()
    
    if not is_super_admin:
        return Response(
            {'detail': 'You do not have permission to view all modules.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    modules = Module.objects.filter(is_active=True)
    modules_data = []
    
    for module in modules:
        stats = get_module_stats(module.id)
        if stats:
            modules_data.append(stats)
    
    return Response(modules_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def module_dashboard(request, module_id):
    """Get module-specific dashboard."""
    # Check if user has access to this module
    has_access = request.user.is_superuser or UserModuleRole.objects.filter(
        user=request.user,
        module_id=module_id
    ).exists()
    
    if not has_access:
        return Response(
            {'detail': 'You do not have access to this module.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = get_module_stats(module_id)
    if not stats:
        return Response(
            {'detail': 'Module not found or inactive.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    category_breakdown = get_module_category_breakdown(module_id)
    
    # Get template code from query params
    template_code = request.query_params.get('template_code')
    
    # Get category-wise and standard-wise completion
    category_completion = get_module_category_completion(module_id, template_code=template_code)
    standard_completion = get_module_standard_completion(module_id, template_code=template_code)
    
    # Get overdue assignments
    overdue_assignments = get_overdue_assignments(module_id, template_code=template_code)
    
    # Calculate overall completion
    templates = ProformaTemplate.objects.filter(module_id=module_id, is_active=True)
    if template_code:
        templates = templates.filter(code=template_code)
    
    overall_completion = stats.get('overall_completion_percent', 0)
    if templates.exists():
        template = templates.first()
        assignments = Assignment.objects.filter(proforma_template=template)
        if assignments.exists():
            score_data = calculate_template_score(template, assignments)
            overall_completion = score_data.get('score_percent', 0)
    
    response_data = {
        **stats,
        'category_breakdown': category_breakdown,
        'category_completion': category_completion,
        'standard_completion': standard_completion,
        'overdue_assignments': overdue_assignments,
        'overall_completion': overall_completion,
    }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_assignments(request):
    """Get current user's assignments across modules."""
    module_id = request.query_params.get('module')
    
    assignments = get_user_assignments(request.user, module_id=module_id)
    
    return Response(assignments)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_stats(request):
    """Get template-specific statistics."""
    template_code = request.query_params.get('template_code')
    template_id = request.query_params.get('template_id')
    module_code = request.query_params.get('module_code')
    
    stats = get_template_stats(
        template_code=template_code,
        template_id=template_id,
        module_code=module_code
    )
    
    if not stats:
        return Response(
            {'detail': 'Template not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(stats)
