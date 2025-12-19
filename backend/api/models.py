from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib


class Project(models.Model):
    """Project model for compliance/accreditation projects."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Google Drive integration
    google_drive_root_folder_id = models.CharField(max_length=255, blank=True, null=True, help_text="Google Drive root folder ID for this project")
    google_drive_oauth_token = models.JSONField(blank=True, null=True, help_text="OAuth token data for Google Drive access")
    google_drive_linked_at = models.DateTimeField(blank=True, null=True, help_text="When Google Drive was linked")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Section(models.Model):
    """Section model for organizing standards within a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = [['project', 'name']]
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Standard(models.Model):
    """Standard model for organizing indicators within a section."""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='standards')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = [['section', 'name']]
    
    def __str__(self):
        return f"{self.section.name} - {self.name}"


class Indicator(models.Model):
    """Indicator/Requirement model for checklist items."""
    
    STATUS_CHOICES = [
        ('not_compliant', 'Not Compliant'),
        ('in_process', 'In Process'),
        ('needs_more_evidence', 'Needs More Evidence'),
        ('compliant', 'Compliant'),
        # Keep old statuses for backwards compatibility
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('non_compliant', 'Non-Compliant'),
    ]
    
    SCHEDULE_TYPE_CHOICES = [
        ('one_time', 'One Time'),
        ('recurring', 'Recurring'),
    ]
    
    EVIDENCE_MODE_CHOICES = [
        ('file_only', 'File Only'),
        ('text_only', 'Text Only'),
        ('hybrid', 'Hybrid (Text + Optional File)'),
        ('frequency_log', 'Frequency Log'),
    ]
    
    # Core fields
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='indicators')
    
    # New structured relationships (nullable for backwards compatibility)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='indicators')
    standard = models.ForeignKey(Standard, on_delete=models.SET_NULL, null=True, blank=True, related_name='indicators')
    
    # Legacy fields (kept for backwards compatibility)
    area = models.CharField(max_length=255, blank=True, help_text="Legacy field, use Section model instead")
    regulation_or_standard = models.CharField(max_length=255, blank=True, help_text="Legacy field, use Standard model instead")
    
    # Indicator details
    requirement = models.TextField()
    evidence_required = models.TextField(blank=True)
    responsible_person = models.CharField(max_length=255, blank=True)
    
    # Frequency and scheduling
    frequency = models.CharField(max_length=100, blank=True, help_text="Original frequency text from CSV")
    normalized_frequency = models.CharField(max_length=50, blank=True, help_text="AI-normalized frequency: Daily, Weekly, Monthly, Quarterly, Annual, etc.")
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES, default='one_time')
    next_due_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Status and scoring
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='not_compliant')
    score = models.IntegerField(default=10, help_text="Score awarded when compliant")
    compliance_notes = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.CharField(max_length=255, blank=True, help_text="Email or username")
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_indicators')
    
    # Evidence mode configuration
    evidence_mode = models.CharField(max_length=20, choices=EVIDENCE_MODE_CHOICES, default='hybrid', help_text="How evidence is expected for this indicator")
    indicator_code = models.CharField(max_length=100, blank=True, help_text="Code for folder naming (e.g., 'IND-001')")
    
    # Idempotency and AI
    indicator_key = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True, help_text="Hash for idempotent imports")
    ai_analysis_data = models.JSONField(null=True, blank=True, help_text="AI analysis output for audit")
    ai_confidence_score = models.FloatField(null=True, blank=True, help_text="AI confidence level")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.requirement[:50]}"
    
    def save(self, *args, **kwargs):
        # Generate indicator_key if not set
        if not self.indicator_key:
            self.indicator_key = self.generate_indicator_key()
        super().save(*args, **kwargs)
    
    def generate_indicator_key(self):
        """Generate deterministic key for idempotent imports."""
        section_name = self.section.name if self.section else (self.area or '')
        standard_name = self.standard.name if self.standard else (self.regulation_or_standard or '')
        
        key_string = f"{self.project_id}:{section_name}:{standard_name}:{self.requirement}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    @staticmethod
    def generate_indicator_key_static(project_id, section_name, standard_name, requirement):
        """Generate deterministic key for idempotent imports (static version)."""
        section_name = section_name or ''
        standard_name = standard_name or ''
        key_string = f"{project_id}:{section_name}:{standard_name}:{requirement}"
        return hashlib.sha256(key_string.encode()).hexdigest()


class Evidence(models.Model):
    """Evidence model for supporting documents and links."""
    
    EVIDENCE_TYPE_CHOICES = [
        ('file', 'File'),
        ('text_declaration', 'Text Declaration'),
        ('hybrid', 'Hybrid'),
        ('form_submission', 'Form Submission'),
    ]
    
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='evidence')
    title = models.CharField(max_length=255)
    
    # Evidence type
    evidence_type = models.CharField(max_length=20, choices=EVIDENCE_TYPE_CHOICES, default='file', help_text="Type of evidence")
    
    # Google Drive integration (replaces file upload)
    google_drive_file_id = models.CharField(max_length=255, blank=True, null=True, help_text="Google Drive file ID")
    google_drive_file_name = models.CharField(max_length=255, blank=True, null=True, help_text="Google Drive file name")
    google_drive_file_url = models.URLField(blank=True, null=True, help_text="Google Drive sharing link")
    
    # Text-only evidence (for physical evidence declarations)
    evidence_text = models.TextField(blank=True, null=True, help_text="Text declaration for physical evidence")
    
    # Period coverage (for frequency-based evidence)
    period_start = models.DateField(blank=True, null=True, help_text="Period start date for frequency-based evidence")
    period_end = models.DateField(blank=True, null=True, help_text="Period end date for frequency-based evidence")
    
    # Digital form submission
    form_data = models.JSONField(blank=True, null=True, help_text="Form submission data")
    form_template = models.ForeignKey('DigitalFormTemplate', on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions', help_text="Form template used for this submission")
    
    # Legacy fields (deprecated but kept for backwards compatibility)
    file = models.FileField(upload_to='evidence/', blank=True, null=True, help_text="DEPRECATED: Use Google Drive instead")
    url = models.URLField(blank=True, help_text="DEPRECATED: Use google_drive_file_url instead")
    
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_evidence')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = 'Evidence'
    
    def __str__(self):
        return f"{self.title} - {self.indicator.requirement[:30]}"


class IndicatorStatusHistory(models.Model):
    """Track status changes for indicators."""
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=25)
    new_status = models.CharField(max_length=25)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Indicator Status Histories'
    
    def __str__(self):
        return f"{self.indicator.requirement[:30]} - {self.old_status} -> {self.new_status}"


class FrequencyLog(models.Model):
    """Track compliance for recurring indicators by period."""
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='frequency_logs')
    period_start = models.DateField()
    period_end = models.DateField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    is_compliant = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = [['indicator', 'period_start', 'period_end']]
    
    def __str__(self):
        return f"{self.indicator.requirement[:30]} - {self.period_start} to {self.period_end}"


class DigitalFormTemplate(models.Model):
    """Template for digital forms used for recurring evidence collection."""
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='form_templates')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    form_fields = models.JSONField(help_text="Field definitions for the form")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_form_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.indicator.requirement[:30]}"


class EvidencePeriod(models.Model):
    """Track expected vs actual evidence for frequency-based indicators."""
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='evidence_periods')
    period_start = models.DateField()
    period_end = models.DateField()
    expected_evidence_count = models.IntegerField(default=1, help_text="Expected number of evidence entries for this period")
    actual_evidence_count = models.IntegerField(default=0, help_text="Actual number of evidence entries (computed)")
    is_compliant = models.BooleanField(default=False, help_text="Whether this period is compliant (computed)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = [['indicator', 'period_start', 'period_end']]
    
    def __str__(self):
        return f"{self.indicator.requirement[:30]} - {self.period_start} to {self.period_end}"


class GoogleDriveFolderCache(models.Model):
    """Cache for Google Drive folder IDs to enable idempotent folder creation."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='drive_folder_cache')
    folder_path = models.CharField(max_length=500, help_text="Path like 'Section/Standard/Indicator'")
    google_drive_folder_id = models.CharField(max_length=255, help_text="Google Drive folder ID")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['project', 'folder_path']]
    
    def __str__(self):
        return f"{self.project.name} - {self.folder_path}"
