"""
Views for evidence app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Evidence
from .serializers import EvidenceSerializer
from assignments.models import ItemStatus
from accounts.permissions import IsQAAdmin, IsDepartmentCoordinator


class EvidenceViewSet(viewsets.ModelViewSet):
    """ViewSet for Evidence operations."""
    queryset = Evidence.objects.select_related('item_status', 'uploaded_by').all()
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'delete']
    
    def get_permissions(self):
        """Override permissions."""
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsAuthenticated()]  # Will check in create/delete
    
    def get_queryset(self):
        """Filter by item_status if provided."""
        queryset = super().get_queryset()
        item_status_id = self.request.query_params.get('item_status')
        if item_status_id:
            queryset = queryset.filter(item_status_id=item_status_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Upload evidence file."""
        # Get item_status_id from URL kwargs (nested route) or request data
        item_status_id = self.kwargs.get('item_status_id') or request.data.get('item_status')
        if not item_status_id:
            return Response(
                {'detail': 'item_status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item_status = ItemStatus.objects.select_related('assignment__department').get(id=item_status_id)
        except ItemStatus.DoesNotExist:
            return Response(
                {'detail': 'ItemStatus not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        is_qa_admin = request.user.is_superuser or request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()
        
        is_coordinator = request.user.user_roles.filter(
            role__name='DepartmentCoordinator',
            department=item_status.assignment.department
        ).exists()
        
        if not (is_qa_admin or is_coordinator):
            return Response(
                {'detail': 'You do not have permission to upload evidence for this item.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate file
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'detail': 'File is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            return Response(
                {'detail': 'File size exceeds 10MB limit'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check allowed MIME types
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/png',
            'text/plain',
        ]
        if file.content_type not in allowed_types:
            return Response(
                {'detail': f'File type {file.content_type} not allowed. Allowed types: {", ".join(allowed_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create evidence
        data = request.data.copy()
        data['item_status'] = item_status_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(uploaded_by=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """Delete evidence with permission check."""
        evidence = self.get_object()
        item_status = evidence.item_status
        
        # Check permissions
        is_qa_admin = request.user.is_superuser or request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists()
        
        is_coordinator = request.user.user_roles.filter(
            role__name='DepartmentCoordinator',
            department=item_status.assignment.department
        ).exists()
        
        is_uploader = evidence.uploaded_by == request.user
        
        if not (is_qa_admin or (is_coordinator and is_uploader)):
            return Response(
                {'detail': 'You do not have permission to delete this evidence.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete file
        evidence.file.delete(save=False)
        evidence.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
