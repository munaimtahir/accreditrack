"""
Proformas app models: ProformaTemplate, ProformaSection, ProformaItem
"""
from django.db import models
from core.models import BaseModel


class ProformaTemplate(BaseModel):
    """Proforma template model."""
    code = models.CharField(max_length=100, unique=True, blank=True, null=True)  # e.g., "PHC-MSDS-2018"
    title = models.CharField(max_length=255)
    authority_name = models.CharField(max_length=255)  # e.g., "PHC", "PMDC"
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
    SECTION_TYPE_CHOICES = [
        ('CATEGORY', 'Category'),
        ('STANDARD', 'Standard'),
    ]
    
    template = models.ForeignKey(
        ProformaTemplate,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )  # For hierarchical structure: category -> standards
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPE_CHOICES,
        default='STANDARD'
    )  # CATEGORY or STANDARD
    code = models.CharField(max_length=50)  # e.g., "ROM", "ROM-1"
    title = models.CharField(max_length=255)
    weight = models.IntegerField(default=0)  # For ordering
    
    class Meta:
        db_table = 'proforma_sections'
        ordering = ['weight', 'code']
        unique_together = [['template', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.title}"


class ProformaItem(BaseModel):
    """Proforma item model (represents indicators in PHC context)."""
    section = models.ForeignKey(
        ProformaSection,
        on_delete=models.CASCADE,
        related_name='items'
    )
    code = models.CharField(max_length=50)  # e.g., "ROM-1-1", "ROM-1-2"
    requirement_text = models.TextField()
    required_evidence_type = models.CharField(max_length=255, blank=True)  # Free text
    importance_level = models.SmallIntegerField(null=True, blank=True)  # 1-5, optional
    implementation_criteria = models.TextField(blank=True)  # Optional implementation criteria
    max_score = models.SmallIntegerField(default=10)  # Maximum score for this indicator
    weightage_percent = models.SmallIntegerField(default=100)  # Weightage percentage (80, 100, etc.)
    is_licensing_critical = models.BooleanField(default=False)  # Whether this is critical for licensing
    
    class Meta:
        db_table = 'proforma_items'
        ordering = ['code']
        unique_together = [['section', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.requirement_text[:50]}"
