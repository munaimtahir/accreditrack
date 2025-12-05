"""
Serializers for comments app.
"""
from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    author_email = serializers.CharField(source='author.email', read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'item_status', 'text', 'type', 'author', 'author_email',
            'author_name', 'created_at'
        ]
        read_only_fields = ['id', 'author', 'created_at']
