from django.contrib import admin
from .models import Project, Indicator, Evidence


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['requirement', 'project', 'status', 'responsible_person', 'created_at']
    search_fields = ['requirement', 'area', 'regulation_or_standard']
    list_filter = ['status', 'project', 'created_at']
    raw_id_fields = ['project']


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'indicator', 'uploaded_at']
    search_fields = ['title', 'notes']
    list_filter = ['uploaded_at']
    raw_id_fields = ['indicator']
