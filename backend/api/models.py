from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    """Project model for compliance/accreditation projects."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Indicator(models.Model):
    """Indicator/Requirement model for checklist items."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='indicators')
    area = models.CharField(max_length=255, blank=True)
    regulation_or_standard = models.CharField(max_length=255, blank=True)
    requirement = models.TextField()
    evidence_required = models.TextField(blank=True)
    responsible_person = models.CharField(max_length=255, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.requirement[:50]}"


class Evidence(models.Model):
    """Evidence model for supporting documents and links."""
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='evidence')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='evidence/', blank=True, null=True)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = 'Evidence'
    
    def __str__(self):
        return f"{self.title} - {self.indicator.requirement[:30]}"
