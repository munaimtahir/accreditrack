"""
Assignments app models: Assignment, ItemStatus
"""
from django.db import models
from core.models import BaseModel


class Assignment(BaseModel):
    """Assignment model linking a proforma template to a department."""
    STATUS_CHOICES = [
        ('NotStarted', 'Not Started'),
        ('InProgress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    proforma_template = models.ForeignKey(
        'proformas.ProformaTemplate',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NotStarted')
    
    class Meta:
        db_table = 'assignments'
        ordering = ['-created_at']
        unique_together = [['proforma_template', 'department']]
    
    def __str__(self):
        return f"{self.proforma_template.title} - {self.department.name}"


class ItemStatus(BaseModel):
    """ItemStatus model tracking the status of each item in an assignment."""
    STATUS_CHOICES = [
        ('NotStarted', 'Not Started'),
        ('InProgress', 'In Progress'),
        ('Submitted', 'Submitted'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NotStarted')
    completion_percent = models.SmallIntegerField(default=0)  # 0-100
    last_updated_by = models.ForeignKey(
        'accounts.User',
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
