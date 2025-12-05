"""
Proformas app models: ProformaTemplate, ProformaSection, ProformaItem
"""
from django.db import models
from core.models import BaseModel


class ProformaTemplate(BaseModel):
    """Proforma template model."""
    title = models.CharField(max_length=255)
    authority_name = models.CharField(max_length=255)  # e.g., "PMDC"
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, default='1.0')
    is_active = models.BooleanField(default=True)
    module = models.ForeignKey(
        'modules.Module',
        on_delete=models.SET_NULL,
        related_name='templates',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'proforma_templates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.authority_name})"


class ProformaSection(BaseModel):
    """Proforma section model."""
    template = models.ForeignKey(
        ProformaTemplate,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    code = models.CharField(max_length=50)  # e.g., "A", "B1", "1.2"
    title = models.CharField(max_length=255)
    weight = models.IntegerField(default=0)  # For ordering
    
    class Meta:
        db_table = 'proforma_sections'
        ordering = ['weight', 'code']
        unique_together = [['template', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.title}"


class ProformaItem(BaseModel):
    """Proforma item model."""
    section = models.ForeignKey(
        ProformaSection,
        on_delete=models.CASCADE,
        related_name='items'
    )
    code = models.CharField(max_length=50)  # e.g., "A.1", "B.2.3"
    requirement_text = models.TextField()
    required_evidence_type = models.CharField(max_length=255, blank=True)  # Free text
    importance_level = models.SmallIntegerField(null=True, blank=True)  # 1-5, optional
    implementation_criteria = models.TextField(blank=True)  # Optional implementation criteria
    
    class Meta:
        db_table = 'proforma_items'
        ordering = ['code']
        unique_together = [['section', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.requirement_text[:50]}"
