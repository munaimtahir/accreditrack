"""
Service functions for assignments app.
"""
from django.db.models import Q, Count, Exists, OuterRef
from .models import Assignment, ItemStatus, AssignmentUpdate
from evidence.models import Evidence


def calculate_indicator_status(item_status):
    """
    Calculate indicator status based on evidence and assignment status.
    
    Returns: NOT_ASSIGNED | NotStarted | InProgress | Submitted | Verified | Rejected
    """
    if not item_status:
        return 'NOT_ASSIGNED'
    
    # Check if verified
    if item_status.status == 'Verified':
        return 'Verified'
    
<<<<<<< HEAD
    # Check if submitted/pending review
=======
    # Check if submitted
>>>>>>> c21e4e8af50074417f4badf980b8cc253535c211
    if item_status.status == 'Submitted':
        return 'Submitted'
    
    # Check if rejected
    if item_status.status == 'Rejected':
        return 'Rejected'
    
    # Check if evidence exists
    has_evidence = Evidence.objects.filter(item_status=item_status).exists()
    
    if has_evidence:
        return 'InProgress'
    
    # Default to not started
    return 'NotStarted'


def update_assignment_status(assignment, new_status, user, note=''):
    """
    Update assignment status and create AssignmentUpdate log.
    """
    assignment.status = new_status
    assignment.save()
    
    # Create update log
    AssignmentUpdate.objects.create(
        assignment=assignment,
        user=user,
        status=new_status,
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
    
<<<<<<< HEAD
    # Check if all items are verified - set assignment to Completed
=======
    # Check if all items are verified
>>>>>>> c21e4e8af50074417f4badf980b8cc253535c211
    all_verified = all(item.status == 'Verified' for item in item_statuses)
    if all_verified and assignment.status != 'Completed':
        assignment.status = 'Completed'
        assignment.save()
        return
    
<<<<<<< HEAD
    # Check if any items are submitted - set assignment to InProgress (under review)
=======
    # Check if any items are submitted
>>>>>>> c21e4e8af50074417f4badf980b8cc253535c211
    any_submitted = any(item.status == 'Submitted' for item in item_statuses)
    if any_submitted and assignment.status == 'NotStarted':
        assignment.status = 'InProgress'
        assignment.save()
        return
    
    # Check if any evidence exists
    has_evidence = Evidence.objects.filter(
        item_status__assignment=assignment
    ).exists()
    
    if has_evidence and assignment.status == 'NotStarted':
        assignment.status = 'InProgress'
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
            'completion_percent': 0,
        }
    
    verified = item_statuses.filter(status='Verified').count()
<<<<<<< HEAD
    pending_review = item_statuses.filter(status='Submitted').count()
=======
    submitted = item_statuses.filter(status='Submitted').count()
>>>>>>> c21e4e8af50074417f4badf980b8cc253535c211
    in_progress = item_statuses.filter(status='InProgress').count()
    not_started = item_statuses.filter(status='NotStarted').count()
    
    return {
        'total': total,
        'verified': verified,
<<<<<<< HEAD
        'pending_review': pending_review,
=======
        'submitted': submitted,
>>>>>>> c21e4e8af50074417f4badf980b8cc253535c211
        'in_progress': in_progress,
        'not_started': not_started,
        'completion_percent': int((verified / total) * 100) if total > 0 else 0,
    }
