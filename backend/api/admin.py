from django.contrib import admin
from .models import Project, Indicator, Evidence, Section, Standard, IndicatorStatusHistory, FrequencyLog


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


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
    list_display = ['title', 'indicator', 'uploaded_by', 'uploaded_at']
    search_fields = ['title', 'notes']
    list_filter = ['uploaded_at']
    raw_id_fields = ['indicator', 'uploaded_by']


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
