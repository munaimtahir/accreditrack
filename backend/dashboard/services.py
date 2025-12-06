"""
Service functions for dashboard analytics.
"""
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import date
from assignments.models import Assignment, ItemStatus
from proformas.models import ProformaTemplate, ProformaSection, ProformaItem
from modules.models import Module, UserModuleRole
from evidence.models import Evidence


def calculate_assignment_completion(assignment):
    """Calculate completion percentage for an assignment."""
    total_items = assignment.item_statuses.count()
    if total_items == 0:
        return 0
    
    verified_items = assignment.item_statuses.filter(status='Verified').count()
    return int((verified_items / total_items) * 100) if total_items > 0 else 0


def calculate_section_completion(assignment, section):
    """Calculate completion percentage for a section within an assignment."""
    section_items = assignment.item_statuses.filter(
        proforma_item__section=section
    )
    total = section_items.count()
    if total == 0:
        return 0
    
    verified = section_items.filter(status='Verified').count()
    return int((verified / total) * 100) if total > 0 else 0


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
    
    # Use aggregate query to get all counts in one database round-trip
    stats = item_statuses.aggregate(
        verified=Count('id', filter=Q(status='Verified')),
        submitted=Count('id', filter=Q(status='Submitted')),
        in_progress=Count('id', filter=Q(status='InProgress')),
        not_started=Count('id', filter=Q(status='NotStarted')),
        rejected=Count('id', filter=Q(status='Rejected')),
    )
    
    return {
        'overall_completion_percent': calculate_assignment_completion(assignment),
        'verified_count': stats['verified'],
        'submitted_count': stats['submitted'],
        'in_progress_count': stats['in_progress'],
        'not_started_count': stats['not_started'],
        'rejected_count': stats['rejected'],
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


def get_module_stats(module_id):
    """Get overall statistics for a module."""
    try:
        module = Module.objects.get(id=module_id, is_active=True)
    except Module.DoesNotExist:
        return None
    
    # Get all templates for this module
    templates = ProformaTemplate.objects.filter(module=module, is_active=True)
    template_ids = list(templates.values_list('id', flat=True))
    
    # Get all assignments for these templates
    assignments = Assignment.objects.filter(proforma_template_id__in=template_ids)
    
    # Get all item statuses for these assignments
    item_statuses = ItemStatus.objects.filter(assignment__in=assignments)
    total_items = item_statuses.count()
    
    if total_items == 0:
        return {
            'module_id': str(module.id),
            'module_code': module.code,
            'module_display_name': module.display_name,
            'total_assignments': 0,
            'total_items': 0,
            'overall_completion_percent': 0,
            'verified_count': 0,
            'submitted_count': 0,
            'in_progress_count': 0,
            'not_started_count': 0,
            'templates_count': templates.count(),
        }
    
    # Use aggregate query to get all counts in one database round-trip
    module_stats = item_statuses.aggregate(
        verified=Count('id', filter=Q(status='Verified')),
        submitted=Count('id', filter=Q(status='Submitted')),
        in_progress=Count('id', filter=Q(status='InProgress')),
        not_started=Count('id', filter=Q(status='NotStarted')),
        rejected=Count('id', filter=Q(status='Rejected')),
    )
    
    return {
        'module_id': str(module.id),
        'module_code': module.code,
        'module_display_name': module.display_name,
        'total_assignments': assignments.count(),
        'total_items': total_items,
        'overall_completion_percent': int((module_stats['verified'] / total_items) * 100) if total_items > 0 else 0,
        'verified_count': module_stats['verified'],
        'submitted_count': module_stats['submitted'],
        'in_progress_count': module_stats['in_progress'],
        'not_started_count': module_stats['not_started'],
        'rejected_count': module_stats['rejected'],
        'templates_count': templates.count(),
    }


def get_module_category_breakdown(module_id):
    """Get category-wise breakdown for a module."""
    try:
        module = Module.objects.get(id=module_id, is_active=True)
    except Module.DoesNotExist:
        return []
    
    # Get all templates for this module
    templates = ProformaTemplate.objects.filter(module=module, is_active=True)
    template_ids = list(templates.values_list('id', flat=True))
    
    # Get all assignments for these templates
    assignments = Assignment.objects.filter(proforma_template_id__in=template_ids)
    
    # Get sections (categories) from templates
    sections = ProformaSection.objects.filter(
        template_id__in=template_ids
    ).distinct().order_by('weight', 'code')
    
    breakdown = []
    for section in sections:
        # Get item statuses for this section
        section_item_statuses = ItemStatus.objects.filter(
            assignment__in=assignments,
            proforma_item__section=section
        )
        total = section_item_statuses.count()
        
        if total == 0:
            continue
        
        # Use aggregate query to get all counts in one database round-trip
        section_stats = section_item_statuses.aggregate(
            verified=Count('id', filter=Q(status='Verified')),
            submitted=Count('id', filter=Q(status='Submitted')),
            in_progress=Count('id', filter=Q(status='InProgress')),
            not_started=Count('id', filter=Q(status='NotStarted')),
            rejected=Count('id', filter=Q(status='Rejected')),
        )
        
        breakdown.append({
            'section_code': section.code,
            'section_title': section.title,
            'total_items': total,
            'verified_count': section_stats['verified'],
            'pending_review_count': section_stats['pending_review'],
            'in_progress_count': section_stats['in_progress'],
            'not_started_count': section_stats['not_started'],
            'completed_count': section_stats['completed'],
            'rejected_count': section_stats['rejected'],
            'completion_percent': int((section_stats['verified'] / total) * 100) if total > 0 else 0,
        })
    
    return breakdown


def get_user_assignments(user, module_id=None):
    """Get user's assignments, optionally filtered by module."""
    assignments = Assignment.objects.filter(
        assigned_to=user
    ).select_related(
        'proforma_template__module', 'department', 'section', 'proforma_item'
    ).prefetch_related('item_statuses')
    
    if module_id:
        assignments = assignments.filter(proforma_template__module_id=module_id)
    
    result = []
    for assignment in assignments:
        total_items = assignment.item_statuses.count()
        verified_items = assignment.item_statuses.filter(status='Verified').count()
        completion_percent = int((verified_items / total_items) * 100) if total_items > 0 else 0
        
        result.append({
            'id': str(assignment.id),
            'proforma_template_id': str(assignment.proforma_template.id),
            'proforma_template_title': assignment.proforma_template.title,
            'module_id': str(assignment.proforma_template.module.id) if assignment.proforma_template.module else None,
            'module_code': assignment.proforma_template.module.code if assignment.proforma_template.module else None,
            'scope_type': assignment.scope_type,
            'section_code': assignment.section.code if assignment.section else None,
            'proforma_item_code': assignment.proforma_item.code if assignment.proforma_item else None,
            'instructions': assignment.instructions,
            'start_date': assignment.start_date,
            'due_date': assignment.due_date,
            'status': assignment.status,
            'total_items': total_items,
            'verified_items': verified_items,
            'completion_percent': completion_percent,
        })
    
    return result


def get_template_stats(template_code=None, template_id=None, module_code=None):
    """Get template-specific statistics including total indicators, assigned indicators, and indicators with evidence."""
    from evidence.models import Evidence
    
    # Get template
    if template_id:
        try:
            template = ProformaTemplate.objects.get(id=template_id, is_active=True)
        except ProformaTemplate.DoesNotExist:
            return None
    elif template_code:
        try:
            template = ProformaTemplate.objects.get(code=template_code, is_active=True)
        except ProformaTemplate.DoesNotExist:
            return None
    elif module_code:
        # Get first template for module
        templates = ProformaTemplate.objects.filter(module__code=module_code, is_active=True)
        if not templates.exists():
            return None
        template = templates.first()
    else:
        return None
    
    # Get all indicators (items) in the template
    total_indicators = ProformaItem.objects.filter(section__template=template).count()
    
    # Get indicators that have at least one assignment
    assigned_indicators = ProformaItem.objects.filter(
        section__template=template,
        item_statuses__isnull=False
    ).distinct().count()
    
    # Get indicators that have at least one evidence record
    indicators_with_evidence = ProformaItem.objects.filter(
        section__template=template,
        item_statuses__evidence_files__isnull=False
    ).distinct().count()
    
    return {
        'template_id': str(template.id),
        'template_code': template.code,
        'template_title': template.title,
        'total_indicators': total_indicators,
        'assigned_indicators': assigned_indicators,
        'indicators_with_evidence': indicators_with_evidence,
    }


def get_module_category_completion(module_id, template_code=None):
    """
    Get category-wise completion for a module.
    Returns list of categories with total/verified indicators and completion %.
    """
    try:
        module = Module.objects.get(id=module_id, is_active=True)
    except Module.DoesNotExist:
        return []
    
    # Get templates for this module
    templates = ProformaTemplate.objects.filter(module=module, is_active=True)
    if template_code:
        templates = templates.filter(code=template_code)
    
    template_ids = list(templates.values_list('id', flat=True))
    if not template_ids:
        return []
    
    # Get all assignments for these templates
    assignments = Assignment.objects.filter(proforma_template_id__in=template_ids)
    
    # Get category sections (section_type='CATEGORY')
    categories = ProformaSection.objects.filter(
        template_id__in=template_ids,
        section_type='CATEGORY',
        parent__isnull=True
    ).order_by('weight', 'code')
    
    result = []
    for category in categories:
        # Get all indicators under this category (through standards)
        standards = category.children.all()
        standard_ids = list(standards.values_list('id', flat=True))
        
        # Get all items (indicators) under these standards
        indicators = ProformaItem.objects.filter(section_id__in=standard_ids)
        total_indicators = indicators.count()
        
        # Get item statuses for these indicators
        item_statuses = ItemStatus.objects.filter(
            assignment__in=assignments,
            proforma_item__in=indicators
        )
        
        verified_indicators = item_statuses.filter(status='Verified').count()
        total_with_assignments = item_statuses.count()
        
        # Calculate completion: verified / total indicators (including unassigned)
        completion_percent = int((verified_indicators / total_indicators) * 100) if total_indicators > 0 else 0
        
        result.append({
            'code': category.code,
            'title': category.title,
            'total_indicators': total_indicators,
            'verified_indicators': verified_indicators,
            'assigned_indicators': total_with_assignments,
            'completion_percent': completion_percent,
        })
    
    return result


def get_module_standard_completion(module_id, template_code=None):
    """
    Get standard-wise completion for a module.
    Returns list of standards with total/verified indicators and completion %.
    """
    try:
        module = Module.objects.get(id=module_id, is_active=True)
    except Module.DoesNotExist:
        return []
    
    # Get templates for this module
    templates = ProformaTemplate.objects.filter(module=module, is_active=True)
    if template_code:
        templates = templates.filter(code=template_code)
    
    template_ids = list(templates.values_list('id', flat=True))
    if not template_ids:
        return []
    
    # Get all assignments for these templates
    assignments = Assignment.objects.filter(proforma_template_id__in=template_ids)
    
    # Get standard sections (section_type='STANDARD')
    standards = ProformaSection.objects.filter(
        template_id__in=template_ids,
        section_type='STANDARD'
    ).order_by('weight', 'code')
    
    result = []
    for standard in standards:
        # Get all items (indicators) under this standard
        indicators = ProformaItem.objects.filter(section=standard)
        total_indicators = indicators.count()
        
        # Get item statuses for these indicators
        item_statuses = ItemStatus.objects.filter(
            assignment__in=assignments,
            proforma_item__in=indicators
        )
        
        verified_indicators = item_statuses.filter(status='Verified').count()
        
        # Calculate completion: verified / total indicators
        completion_percent = int((verified_indicators / total_indicators) * 100) if total_indicators > 0 else 0
        
        result.append({
            'code': standard.code,
            'title': standard.title,
            'category_code': standard.parent.code if standard.parent else None,
            'category_title': standard.parent.title if standard.parent else None,
            'total_indicators': total_indicators,
            'verified_indicators': verified_indicators,
            'completion_percent': completion_percent,
        })
    
    return result


def get_overdue_assignments(module_id, template_code=None):
    """
    Get overdue assignments for a module.
    Returns list of overdue assignments with indicator details.
    """
    try:
        module = Module.objects.get(id=module_id, is_active=True)
    except Module.DoesNotExist:
        return []
    
    # Get templates for this module
    templates = ProformaTemplate.objects.filter(module=module, is_active=True)
    if template_code:
        templates = templates.filter(code=template_code)
    
    template_ids = list(templates.values_list('id', flat=True))
    if not template_ids:
        return []
    
    # Get overdue assignments (due_date < today and status not Completed)
    today = date.today()
    overdue_assignments = Assignment.objects.filter(
        proforma_template_id__in=template_ids,
        due_date__lt=today
    ).exclude(status='Completed').prefetch_related(
        'item_statuses__proforma_item__section',
        'assigned_to'
    )
    
    result = []
    for assignment in overdue_assignments:
        # Get item statuses for this assignment (already prefetched)
        item_statuses = [is_obj for is_obj in assignment.item_statuses.all() if is_obj.status != 'Verified']
        
        for item_status in item_statuses:
            result.append({
                'assignment_id': str(assignment.id),
                'indicator_code': item_status.proforma_item.code,
                'indicator_text': item_status.proforma_item.requirement_text[:100],
                'section_code': item_status.proforma_item.section.code,
                'due_date': assignment.due_date,
                'status': item_status.status,
                'assigned_to': [u.email for u in assignment.assigned_to.all()],
                'department_name': assignment.department.name if assignment.department else None,
            })
    
    return result


def calculate_indicator_score(item_status):
    """
    Calculate score for an indicator.
    Basic scoring: max_score if Verified, 0 otherwise.
    """
    if item_status.status == 'Verified':
        return item_status.proforma_item.max_score
    return 0


def calculate_category_score(category_section, assignments):
    """
    Calculate total score for a category.
    """
    # Get all standards under this category
    standards = category_section.children.all()
    standard_ids = list(standards.values_list('id', flat=True))
    
    # Get all indicators under these standards
    indicators = ProformaItem.objects.filter(section_id__in=standard_ids)
    
    # Get item statuses for these indicators
    item_statuses = ItemStatus.objects.filter(
        assignment__in=assignments,
        proforma_item__in=indicators
    )
    
    # Create dictionary for O(1) lookup instead of N+1 queries
    item_statuses_dict = {item.proforma_item_id: item for item in item_statuses}
    
    total_score = 0
    max_possible_score = 0
    
    for indicator in indicators:
        max_possible_score += indicator.max_score
        item_status = item_statuses_dict.get(indicator.id)
        if item_status:
            total_score += calculate_indicator_score(item_status)
    
    return {
        'score_achieved': total_score,
        'max_possible_score': max_possible_score,
        'score_percent': int((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0,
    }


def calculate_template_score(template, assignments):
    """
    Calculate overall score for a template.
    """
    # Get all categories
    categories = template.sections.filter(section_type='CATEGORY', parent__isnull=True)
    
    total_score = 0
    max_possible_score = 0
    
    for category in categories:
        category_score = calculate_category_score(category, assignments)
        total_score += category_score['score_achieved']
        max_possible_score += category_score['max_possible_score']
    
    return {
        'score_achieved': total_score,
        'max_possible_score': max_possible_score,
        'score_percent': int((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0,
    }
