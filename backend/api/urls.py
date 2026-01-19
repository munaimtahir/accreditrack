"""
URL configuration for the API app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, IndicatorViewSet, EvidenceViewSet,
    SectionViewSet, StandardViewSet, FrequencyLogViewSet,
    DigitalFormTemplateViewSet, EvidencePeriodViewSet,
    PendingDigitalFormTemplateViewSet
)
from . import ai_views
from .views import submit_digital_form

# Create router and register viewsets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'standards', StandardViewSet, basename='standard')
router.register(r'indicators', IndicatorViewSet, basename='indicator')
router.register(r'evidence', EvidenceViewSet, basename='evidence')
router.register(r'frequency-logs', FrequencyLogViewSet, basename='frequency-log')
router.register(r'form-templates', DigitalFormTemplateViewSet, basename='form-template')
router.register(r'pending-form-templates', PendingDigitalFormTemplateViewSet, basename='pending-form-template')
router.register(r'evidence-periods', EvidencePeriodViewSet, basename='evidence-period')

# AI endpoints
ai_patterns = [
    path('analyze-checklist/', ai_views.analyze_checklist, name='analyze-checklist'),
    path('analyze-categorization/', ai_views.analyze_categorization, name='analyze-categorization'),
    path('ask-assistant/', ai_views.ask_assistant, name='ask-assistant'),
    path('report-summary/', ai_views.report_summary, name='report-summary'),
    path('convert-document/', ai_views.convert_document, name='convert-document'),
    path('compliance-guide/', ai_views.compliance_guide, name='compliance-guide'),
    path('analyze-tasks/', ai_views.analyze_tasks, name='analyze-tasks'),
    path('evidence-assistance/', ai_views.evidence_assistance, name='evidence-assistance'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('submit-form/', submit_digital_form, name='submit-form'),
] + ai_patterns
