"""
Views for comments app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Comment
from .serializers import CommentSerializer
from assignments.models import ItemStatus


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment operations."""
    queryset = Comment.objects.select_related('item_status', 'author').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']  # Only allow GET and POST
    
    def get_queryset(self):
        """Filter by item_status if provided."""
        queryset = super().get_queryset()
        # Check if item_status_id is in URL kwargs (from nested route)
        item_status_id = self.kwargs.get('item_status_id') or self.request.query_params.get('item_status')
        if item_status_id:
            queryset = queryset.filter(item_status_id=item_status_id)
        return queryset.order_by('created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a comment."""
        # Get item_status_id from URL kwargs (nested route) or request data
        item_status_id = self.kwargs.get('item_status_id') or request.data.get('item_status')
        if not item_status_id:
            return Response(
                {'detail': 'item_status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item_status = ItemStatus.objects.get(id=item_status_id)
        except ItemStatus.DoesNotExist:
            return Response(
                {'detail': 'ItemStatus not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data.copy()
        data['item_status'] = item_status_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
