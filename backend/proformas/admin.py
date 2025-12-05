from django.contrib import admin
from .models import ProformaTemplate, ProformaSection, ProformaItem


class ProformaItemInline(admin.TabularInline):
    """Inline admin for ProformaItem."""
    model = ProformaItem
    extra = 1


class ProformaSectionInline(admin.TabularInline):
    """Inline admin for ProformaSection."""
    model = ProformaSection
    extra = 1
    show_change_link = True


@admin.register(ProformaTemplate)
class ProformaTemplateAdmin(admin.ModelAdmin):
    """Admin interface for ProformaTemplate model."""
    list_display = ['title', 'authority_name', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'authority_name', 'created_at']
    search_fields = ['title', 'authority_name', 'description']
    inlines = [ProformaSectionInline]


@admin.register(ProformaSection)
class ProformaSectionAdmin(admin.ModelAdmin):
    """Admin interface for ProformaSection model."""
    list_display = ['code', 'title', 'template', 'weight', 'created_at']
    list_filter = ['template', 'created_at']
    search_fields = ['code', 'title', 'template__title']
    autocomplete_fields = ['template']
    inlines = [ProformaItemInline]


@admin.register(ProformaItem)
class ProformaItemAdmin(admin.ModelAdmin):
    """Admin interface for ProformaItem model."""
    list_display = ['code', 'section', 'importance_level', 'created_at']
    list_filter = ['section__template', 'importance_level', 'created_at']
    search_fields = ['code', 'requirement_text', 'section__code']
    autocomplete_fields = ['section']
