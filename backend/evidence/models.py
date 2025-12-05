"""
Evidence app models: Evidence
"""
from django.db import models
from core.models import BaseModel


class Evidence(BaseModel):
    """Evidence model for file uploads linked to ItemStatus."""
    item_status = models.ForeignKey(
        'assignments.ItemStatus',
        on_delete=models.CASCADE,
        related_name='evidence_files'
    )
    file = models.FileField(upload_to='evidence/%Y/%m/%d/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='uploaded_evidence',
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'evidence'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Evidence for {self.item_status.proforma_item.code}"
