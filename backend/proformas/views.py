"""
Views for proformas app.
"""
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ProformaTemplate, ProformaSection, ProformaItem
from .serializers import (
    ProformaTemplateSerializer,
    ProformaTemplateListSerializer,
    ProformaSectionSerializer,
    ProformaItemSerializer
)
from accounts.permissions import IsQAAdmin


class ProformaTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for ProformaTemplate CRUD operations."""
    queryset = ProformaTemplate.objects.prefetch_related('sections__items').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return ProformaTemplateListSerializer
        return ProformaTemplateSerializer
    
    def get_permissions(self):
        """Override to allow read access to all authenticated users."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsQAAdmin()]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        code = self.request.query_params.get('code')
        if code:
            queryset = queryset.filter(code=code)
        
        module_code = self.request.query_params.get('module_code')
        if module_code:
            queryset = queryset.filter(module__code=module_code)
        
        module_id = self.request.query_params.get('module')
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(authority_name__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(code__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['get', 'post'], url_path='sections')
    def sections(self, request, pk=None):
        """Get or create sections for a template."""
        template = self.get_object()
        if request.method == 'GET':
            sections = template.sections.prefetch_related('items').all()
            serializer = ProformaSectionSerializer(sections, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = ProformaSectionSerializer(data={**request.data, 'template': template.id})
            if serializer.is_valid():
                serializer.save(template=template)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProformaSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for ProformaSection CRUD operations."""
    queryset = ProformaSection.objects.prefetch_related('items').all()
    serializer_class = ProformaSectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Override to allow read access to all authenticated users."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsQAAdmin()]
    
    def get_queryset(self):
        """Filter by template if provided."""
        queryset = super().get_queryset()
        template_id = self.request.query_params.get('template')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        return queryset
    
    @action(detail=True, methods=['get', 'post'], url_path='items')
    def items(self, request, pk=None):
        """Get or create items for a section."""
        section = self.get_object()
        if request.method == 'GET':
            items = section.items.all()
            serializer = ProformaItemSerializer(items, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = ProformaItemSerializer(data={**request.data, 'section': section.id})
            if serializer.is_valid():
                serializer.save(section=section)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProformaItemViewSet(viewsets.ModelViewSet):
    """ViewSet for ProformaItem CRUD operations."""
    queryset = ProformaItem.objects.all()
    serializer_class = ProformaItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Override to allow read access to all authenticated users."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsQAAdmin()]
    
    def get_queryset(self):
        """Filter by section if provided."""
        queryset = super().get_queryset()
        section_id = self.request.query_params.get('section')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        return queryset
