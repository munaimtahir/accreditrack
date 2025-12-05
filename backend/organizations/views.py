"""
Views for organizations app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Department
from .serializers import DepartmentSerializer
from accounts.permissions import IsQAAdmin


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department CRUD operations."""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Override to allow read access to all authenticated users."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsQAAdmin()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        
        # QAAdmin and SuperAdmin see all departments
        if self.request.user.is_superuser or self.request.user.user_roles.filter(
            role__name__in=['SuperAdmin', 'QAAdmin']
        ).exists():
            return queryset
        
        # DepartmentCoordinator sees only their assigned department
        user_departments = self.request.user.user_roles.filter(
            role__name='DepartmentCoordinator'
        ).values_list('department_id', flat=True)
        
        if user_departments:
            return queryset.filter(id__in=user_departments)
        
        # Viewer sees all (read-only)
        return queryset
