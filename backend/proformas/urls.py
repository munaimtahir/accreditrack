"""
URLs for proformas app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProformaTemplateViewSet, ProformaSectionViewSet, ProformaItemViewSet

router = DefaultRouter()
router.register(r'templates', ProformaTemplateViewSet, basename='proforma-template')
router.register(r'sections', ProformaSectionViewSet, basename='proforma-section')
router.register(r'items', ProformaItemViewSet, basename='proforma-item')

urlpatterns = [
    path('', include(router.urls)),
]
