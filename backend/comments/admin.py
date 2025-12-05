from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""
    list_display = ['item_status', 'type', 'author', 'created_at']
    list_filter = ['type', 'created_at', 'item_status__assignment__department']
    search_fields = ['text', 'item_status__proforma_item__code', 'author__email']
    autocomplete_fields = ['item_status', 'author']
