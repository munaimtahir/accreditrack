from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    """
    Represents a compliance or accreditation project.

    Each project has a name and a description and serves as a container for
    related compliance indicators.

    Attributes:
        name (CharField): The name of the project.
        description (TextField): A detailed description of the project.
        created_at (DateTimeField): The timestamp when the project was created.
        updated_at (DateTimeField): The timestamp when the project was last updated.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Indicator(models.Model):
    """
    Represents a single compliance indicator or checklist item within a project.

    Attributes:
        project (ForeignKey): The project to which this indicator belongs.
        area (CharField): The compliance area (e.g., 'Safety', 'Documentation').
        regulation_or_standard (CharField): The specific regulation or standard.
        requirement (TextField): The detailed requirement for the indicator.
        evidence_required (TextField): Description of the evidence needed.
        responsible_person (CharField): The person or role responsible.
        frequency (CharField): How often the indicator is checked (e.g., 'Annual').
        status (CharField): The current compliance status of the indicator.
        assigned_to (CharField): The person to whom this indicator is assigned.
        created_at (DateTimeField): The timestamp when the indicator was created.
        updated_at (DateTimeField): The timestamp when the indicator was last updated.
    """
    
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
    """
    Represents evidence for a compliance indicator.

    Evidence can be a file upload, a URL, or textual notes.

    Attributes:
        indicator (ForeignKey): The indicator this evidence supports.
        title (CharField): The title of the evidence.
        file (FileField): An uploaded file.
        url (URLField): A URL pointing to external evidence.
        notes (TextField): Textual notes or descriptions.
        uploaded_at (DateTimeField): The timestamp when the evidence was uploaded.
    """
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
