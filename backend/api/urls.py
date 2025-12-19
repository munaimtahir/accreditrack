"""
URL configuration for the API app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, IndicatorViewSet, EvidenceViewSet,
    SectionViewSet, StandardViewSet, FrequencyLogViewSet
)
from . import ai_views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'standards', StandardViewSet, basename='standard')
router.register(r'indicators', IndicatorViewSet, basename='indicator')
router.register(r'evidence', EvidenceViewSet, basename='evidence')
router.register(r'frequency-logs', FrequencyLogViewSet, basename='frequency-log')

# AI endpoints
ai_patterns = [
    path('analyze-checklist/', ai_views.analyze_checklist, name='analyze-checklist'),
    path('analyze-categorization/', ai_views.analyze_categorization, name='analyze-categorization'),
    path('ask-assistant/', ai_views.ask_assistant, name='ask-assistant'),
    path('report-summary/', ai_views.report_summary, name='report-summary'),
    path('convert-document/', ai_views.convert_document, name='convert-document'),
    path('compliance-guide/', ai_views.compliance_guide, name='compliance-guide'),
    path('analyze-tasks/', ai_views.analyze_tasks, name='analyze-tasks'),
]

urlpatterns = [
    path('', include(router.urls)),
] + ai_patterns
