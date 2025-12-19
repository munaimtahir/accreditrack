from django.contrib import admin
from .models import (
    Project, Indicator, Evidence, Section, Standard, IndicatorStatusHistory, 
    FrequencyLog, DigitalFormTemplate, EvidencePeriod, GoogleDriveFolderCache
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'google_drive_linked', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'google_drive_linked_at']
    readonly_fields = ['google_drive_linked_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Google Drive Integration', {
            'fields': ('google_drive_root_folder_id', 'google_drive_oauth_token', 'google_drive_linked_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def google_drive_linked(self, obj):
        return bool(obj.google_drive_root_folder_id)
    google_drive_linked.boolean = True
    google_drive_linked.short_description = 'Drive Linked'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['project', 'created_at']
    raw_id_fields = ['project']


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['section__project', 'created_at']
    raw_id_fields = ['section']


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['requirement', 'project', 'section', 'standard', 'status', 'schedule_type', 'next_due_date', 'responsible_person', 'created_at']
    search_fields = ['requirement', 'area', 'regulation_or_standard', 'evidence_required']
    list_filter = ['status', 'schedule_type', 'is_active', 'project', 'section', 'created_at']
    raw_id_fields = ['project', 'section', 'standard', 'assigned_user']
    readonly_fields = ['indicator_key', 'ai_confidence_score']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'section', 'standard', 'requirement', 'evidence_required')
        }),
        ('Legacy Fields', {
            'fields': ('area', 'regulation_or_standard'),
            'classes': ('collapse',)
        }),
        ('Assignment & Responsibility', {
            'fields': ('responsible_person', 'assigned_to', 'assigned_user')
        }),
        ('Scheduling & Frequency', {
            'fields': ('schedule_type', 'frequency', 'normalized_frequency', 'next_due_date', 'is_active')
        }),
        ('Evidence Configuration', {
            'fields': ('evidence_mode', 'indicator_code')
        }),
        ('Status & Scoring', {
            'fields': ('status', 'score', 'compliance_notes')
        }),
        ('AI Analysis', {
            'fields': ('indicator_key', 'ai_analysis_data', 'ai_confidence_score'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'indicator', 'evidence_type', 'uploaded_by', 'uploaded_at']
    search_fields = ['title', 'notes', 'evidence_text']
    list_filter = ['evidence_type', 'uploaded_at']
    raw_id_fields = ['indicator', 'uploaded_by', 'form_template']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('indicator', 'title', 'evidence_type', 'notes')
        }),
        ('Google Drive', {
            'fields': ('google_drive_file_id', 'google_drive_file_name', 'google_drive_file_url'),
            'classes': ('collapse',)
        }),
        ('Text Evidence', {
            'fields': ('evidence_text',),
            'classes': ('collapse',)
        }),
        ('Period Coverage', {
            'fields': ('period_start', 'period_end'),
            'classes': ('collapse',)
        }),
        ('Form Submission', {
            'fields': ('form_template', 'form_data'),
            'classes': ('collapse',)
        }),
        ('Legacy Fields', {
            'fields': ('file', 'url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at')
        }),
    )


@admin.register(IndicatorStatusHistory)
class IndicatorStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'old_status', 'new_status', 'changed_by', 'timestamp']
    search_fields = ['notes']
    list_filter = ['old_status', 'new_status', 'timestamp']
    raw_id_fields = ['indicator', 'changed_by']
    readonly_fields = ['timestamp']


@admin.register(FrequencyLog)
class FrequencyLogAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'period_start', 'period_end', 'is_compliant', 'submitted_by', 'submitted_at']
    search_fields = ['notes']
    list_filter = ['is_compliant', 'submitted_at']
    raw_id_fields = ['indicator', 'submitted_by']
    readonly_fields = ['submitted_at']


@admin.register(DigitalFormTemplate)
class DigitalFormTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'indicator', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    raw_id_fields = ['indicator', 'created_by']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EvidencePeriod)
class EvidencePeriodAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'period_start', 'period_end', 'expected_evidence_count', 'actual_evidence_count', 'is_compliant']
    search_fields = []
    list_filter = ['is_compliant', 'period_start', 'period_end']
    raw_id_fields = ['indicator']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GoogleDriveFolderCache)
class GoogleDriveFolderCacheAdmin(admin.ModelAdmin):
    list_display = ['project', 'folder_path', 'google_drive_folder_id', 'created_at']
    search_fields = ['folder_path', 'google_drive_folder_id']
    list_filter = ['created_at']
    raw_id_fields = ['project']
    readonly_fields = ['created_at']
