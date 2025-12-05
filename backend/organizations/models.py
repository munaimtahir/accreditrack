"""
Organizations app models: Department
"""
from django.db import models
from core.models import BaseModel


class Department(BaseModel):
    """Department model with optional parent for hierarchy."""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
