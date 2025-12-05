"""
Service functions for dashboard analytics.
"""
from django.db.models import Count, Q, Avg
from assignments.models import Assignment, ItemStatus
from proformas.models import ProformaTemplate, ProformaSection


def calculate_assignment_completion(assignment):
    """Calculate completion percentage for an assignment."""
    total_items = assignment.item_statuses.count()
    if total_items == 0:
        return 0
    
    verified_items = assignment.item_statuses.filter(status='Verified').count()
    return int((verified_items / total_items) * 100)


def calculate_section_completion(assignment, section):
    """Calculate completion percentage for a section within an assignment."""
    section_items = assignment.item_statuses.filter(
        proforma_item__section=section
    )
    total = section_items.count()
    if total == 0:
        return 0
    
    verified = section_items.filter(status='Verified').count()
    return int((verified / total) * 100)


def get_assignment_summary(assignment):
    """Get summary statistics for an assignment."""
    item_statuses = assignment.item_statuses.all()
    total = item_statuses.count()
    
    if total == 0:
        return {
            'overall_completion_percent': 0,
            'verified_count': 0,
            'submitted_count': 0,
            'in_progress_count': 0,
            'not_started_count': 0,
            'rejected_count': 0,
        }
    
    return {
        'overall_completion_percent': calculate_assignment_completion(assignment),
        'verified_count': item_statuses.filter(status='Verified').count(),
        'submitted_count': item_statuses.filter(status='Submitted').count(),
        'in_progress_count': item_statuses.filter(status='InProgress').count(),
        'not_started_count': item_statuses.filter(status='NotStarted').count(),
        'rejected_count': item_statuses.filter(status='Rejected').count(),
    }


def get_section_summaries(assignment):
    """Get completion summaries for all sections in an assignment."""
    sections = ProformaSection.objects.filter(
        template=assignment.proforma_template
    ).order_by('weight', 'code')
    
    summaries = []
    for section in sections:
        completion = calculate_section_completion(assignment, section)
        item_statuses = assignment.item_statuses.filter(
            proforma_item__section=section
        )
        
        summaries.append({
            'section': {
                'id': str(section.id),
                'code': section.code,
                'title': section.title,
                'weight': section.weight,
            },
            'completion_percent': completion,
            'total_items': item_statuses.count(),
            'verified_items': item_statuses.filter(status='Verified').count(),
        })
    
    return summaries


def get_pending_items(user, template_id=None, department_id=None):
    """Get list of pending items (not Verified) filtered by user role."""
    # Base queryset
    item_statuses = ItemStatus.objects.select_related(
        'assignment__proforma_template',
        'assignment__department',
        'proforma_item__section'
    ).exclude(status='Verified')
    
    # Filter by template if provided
    if template_id:
        item_statuses = item_statuses.filter(assignment__proforma_template_id=template_id)
    
    # Filter by department if provided
    if department_id:
        item_statuses = item_statuses.filter(assignment__department_id=department_id)
    
    # Apply role-based filtering
    is_qa_admin = user.is_superuser or user.user_roles.filter(
        role__name__in=['SuperAdmin', 'QAAdmin']
    ).exists()
    
    if not is_qa_admin:
        # DepartmentCoordinator sees only their department's items
        user_departments = user.user_roles.filter(
            role__name='DepartmentCoordinator'
        ).values_list('department_id', flat=True)
        
        if user_departments:
            item_statuses = item_statuses.filter(assignment__department_id__in=user_departments)
    
    return item_statuses.order_by('assignment__due_date', 'proforma_item__code')
