"""
URLs for modules app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModuleViewSet, UserModuleRoleViewSet

router = DefaultRouter()
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'user-module-roles', UserModuleRoleViewSet, basename='user-module-role')

urlpatterns = [
    path('', include(router.urls)),
]
