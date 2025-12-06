"""
Assignments app models: Assignment, ItemStatus
"""
from django.db import models
from core.models import BaseModel

# Constants
USER_MODEL = 'accounts.User'


class Assignment(BaseModel):
    """Assignment model linking a proforma template to a department or users."""
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('COMPLETED', 'Completed'),
        ('VERIFIED', 'Verified'),
    ]
    
    SCOPE_TYPE_CHOICES = [
        ('DEPARTMENT', 'Department'),
        ('SECTION', 'Section'),
        ('INDICATOR', 'Indicator'),
    ]
    
    proforma_template = models.ForeignKey(
        'proformas.ProformaTemplate',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.CASCADE,
        related_name='assignments',
        null=True,
        blank=True
    )
    assigned_to = models.ManyToManyField(
        USER_MODEL,
        related_name='assignments',
        blank=True
    )
    scope_type = models.CharField(
        max_length=20,
        choices=SCOPE_TYPE_CHOICES,
        default='DEPARTMENT'
    )
    section = models.ForeignKey(
        'proformas.ProformaSection',
        on_delete=models.CASCADE,
        related_name='assignments',
        null=True,
        blank=True
    )
    proforma_item = models.ForeignKey(
        'proformas.ProformaItem',
        on_delete=models.CASCADE,
        related_name='assignments',
        null=True,
        blank=True
    )
    instructions = models.TextField(blank=True)
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    
    class Meta:
        db_table = 'assignments'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.department:
            return f"{self.proforma_template.title} - {self.department.name}"
        elif self.assigned_to.exists():
            users = ', '.join([u.email for u in self.assigned_to.all()[:3]])
            return f"{self.proforma_template.title} - {users}"
        return f"{self.proforma_template.title} - Assignment"


class ItemStatus(BaseModel):
    """ItemStatus model tracking the status of each item in an assignment."""
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('COMPLETED', 'Completed'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='item_statuses'
    )
    proforma_item = models.ForeignKey(
        'proformas.ProformaItem',
        on_delete=models.CASCADE,
        related_name='item_statuses'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    completion_percent = models.SmallIntegerField(default=0)  # 0-100
    last_updated_by = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='updated_item_statuses',
        null=True
    )
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'item_statuses'
        ordering = ['proforma_item__code']
        unique_together = [['assignment', 'proforma_item']]
    
    def __str__(self):
        return f"{self.assignment} - {self.proforma_item.code} ({self.status})"


class AssignmentUpdate(BaseModel):
    """AssignmentUpdate model for tracking assignment progress updates."""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    user = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_updates'
    )
    status_before = models.CharField(
        max_length=20,
        choices=Assignment.STATUS_CHOICES,
        blank=True
    )
    status_after = models.CharField(
        max_length=20,
        choices=Assignment.STATUS_CHOICES,
        blank=True
    )
    note = models.TextField()
    
    class Meta:
        db_table = 'assignment_updates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.assignment} by {self.user.email}"
