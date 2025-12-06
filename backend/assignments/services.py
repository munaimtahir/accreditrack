"""
Service functions for assignments app.
"""
from django.db.models import Q, Count, Exists, OuterRef
from .models import Assignment, ItemStatus, AssignmentUpdate
from evidence.models import Evidence


def calculate_indicator_status(item_status):
    """
    Calculate indicator status based on evidence and assignment status.
    
    Returns: NOT_ASSIGNED | NOT_STARTED | IN_PROGRESS | PENDING_REVIEW | COMPLETED | VERIFIED
    """
    if not item_status:
        return 'NOT_ASSIGNED'
    
    # Check if verified
    if item_status.status == 'VERIFIED':
        return 'VERIFIED'
    
    # Check if submitted/pending review
    if item_status.status == 'PENDING_REVIEW':
        return 'PENDING_REVIEW'
    
    # Check if completed
    if item_status.status == 'COMPLETED':
        return 'COMPLETED'
    
    # Check if evidence exists
    has_evidence = Evidence.objects.filter(item_status=item_status).exists()
    
    if has_evidence:
        return 'IN_PROGRESS'
    
    # Default to not started
    return 'NOT_STARTED'


def update_assignment_status(assignment, new_status, user, note=''):
    """
    Update assignment status and create AssignmentUpdate log.
    """
    old_status = assignment.status
    assignment.status = new_status
    assignment.save()
    
    # Create update log
    AssignmentUpdate.objects.create(
        assignment=assignment,
        user=user,
        status_before=old_status,
        status_after=new_status,
        note=note
    )
    
    return assignment


def auto_update_assignment_status(assignment):
    """
    Automatically update assignment status based on evidence and item statuses.
    """
    item_statuses = assignment.item_statuses.all()
    
    if not item_statuses.exists():
        return
    
    # Check if all items are verified
    all_verified = all(item.status == 'VERIFIED' for item in item_statuses)
    if all_verified and assignment.status != 'VERIFIED':
        assignment.status = 'VERIFIED'
        assignment.save()
        return
    
    # Check if any items are pending review
    any_pending = any(item.status == 'PENDING_REVIEW' for item in item_statuses)
    if any_pending and assignment.status not in ['PENDING_REVIEW', 'VERIFIED']:
        assignment.status = 'PENDING_REVIEW'
        assignment.save()
        return
    
    # Check if any evidence exists
    has_evidence = Evidence.objects.filter(
        item_status__assignment=assignment
    ).exists()
    
    if has_evidence and assignment.status == 'NOT_STARTED':
        assignment.status = 'IN_PROGRESS'
        assignment.save()
        return


def get_indicator_completion_stats(proforma_item, assignment=None):
    """
    Get completion statistics for a specific indicator.
    """
    if assignment:
        item_statuses = ItemStatus.objects.filter(
            proforma_item=proforma_item,
            assignment=assignment
        )
    else:
        item_statuses = ItemStatus.objects.filter(proforma_item=proforma_item)
    
    total = item_statuses.count()
    if total == 0:
        return {
            'total': 0,
            'verified': 0,
            'pending_review': 0,
            'in_progress': 0,
            'not_started': 0,
            'completed': 0,
            'rejected': 0,
            'completion_percent': 0,
        }
    
    # Use aggregate query to get all counts in one database round-trip
    stats = item_statuses.aggregate(
        verified=Count('id', filter=Q(status='VERIFIED')),
        pending_review=Count('id', filter=Q(status='PENDING_REVIEW')),
        in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
        not_started=Count('id', filter=Q(status='NOT_STARTED')),
        completed=Count('id', filter=Q(status='COMPLETED')),
        rejected=Count('id', filter=Q(status='REJECTED')),
    )
    
    return {
        'total': total,
        'verified': stats['verified'],
        'pending_review': stats['pending_review'],
        'in_progress': stats['in_progress'],
        'not_started': stats['not_started'],
        'completed': stats['completed'],
        'rejected': stats['rejected'],
        'completion_percent': int((stats['verified'] / total) * 100) if total > 0 else 0,
    }
