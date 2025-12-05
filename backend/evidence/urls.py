"""
URLs for evidence app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EvidenceViewSet

router = DefaultRouter()
router.register(r'', EvidenceViewSet, basename='evidence')

urlpatterns = [
    path('', include(router.urls)),
]

# For nested routes from item-status
urlpatterns_nested = [
    path('', EvidenceViewSet.as_view({'get': 'list', 'post': 'create'}), name='evidence-list-create'),
]
