"""
Evidence app models: Evidence
"""
from django.db import models
from core.models import BaseModel


class Evidence(BaseModel):
    """Evidence model for file uploads linked to ItemStatus."""
    EVIDENCE_TYPE_CHOICES = [
        ('file', 'File'),
        ('image', 'Image'),
        ('note', 'Note'),
        ('reference', 'Reference'),
    ]
    
    item_status = models.ForeignKey(
        'assignments.ItemStatus',
        on_delete=models.CASCADE,
        related_name='evidence_files'
    )
    file = models.FileField(upload_to='evidence/%Y/%m/%d/', blank=True, null=True)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)  # Additional notes for evidence
    reference_code = models.CharField(max_length=255, blank=True)  # Reference code for evidence
    evidence_type = models.CharField(
        max_length=20,
        choices=EVIDENCE_TYPE_CHOICES,
        default='file'
    )
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
    
    def clean(self):
        """Validate that note-only evidence doesn't require file."""
        from django.core.exceptions import ValidationError
        if self.evidence_type in ['note', 'reference'] and not self.note and not self.reference_code:
            raise ValidationError('Note or reference code is required for note/reference type evidence.')
        if self.evidence_type in ['file', 'image'] and not self.file:
            raise ValidationError('File is required for file/image type evidence.')
