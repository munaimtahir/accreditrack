from django.contrib import admin
from .models import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    """Admin interface for Evidence model."""
    list_display = ['item_status', 'file', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'item_status__assignment__department']
    search_fields = ['item_status__proforma_item__code', 'description', 'uploaded_by__email']
    autocomplete_fields = ['item_status', 'uploaded_by']
