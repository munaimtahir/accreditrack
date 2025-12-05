"""
URLs for assignments app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, AssignmentUpdateViewSet

router = DefaultRouter()
router.register(r'', AssignmentViewSet, basename='assignment')
router.register(r'updates', AssignmentUpdateViewSet, basename='assignment-update')

urlpatterns = [
    path('', include(router.urls)),
]
