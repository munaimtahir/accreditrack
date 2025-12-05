"""
Comments app models: Comment
"""
from django.db import models
from core.models import BaseModel


class Comment(BaseModel):
    """Comment model linked to ItemStatus."""
    TYPE_CHOICES = [
        ('General', 'General'),
        ('Query', 'Query'),
        ('Clarification', 'Clarification'),
        ('NonComplianceNote', 'Non-Compliance Note'),
    ]
    
    item_status = models.ForeignKey(
        'assignments.ItemStatus',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='General')
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='comments',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.item_status.proforma_item.code} by {self.author.email if self.author else 'Unknown'}"
