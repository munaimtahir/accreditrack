"""
API URL configuration for AccrediTrack v1.
"""
from django.urls import path, include

urlpatterns = [
    path('auth/', include('accounts.urls')),
    path('users/', include('accounts.user_urls')),
    path('departments/', include('organizations.urls')),
    path('proformas/', include('proformas.urls')),
    path('assignments/', include('assignments.urls')),
    path('item-status/', include('assignments.item_status_urls')),
    path('evidence/', include('evidence.urls')),
    path('comments/', include('comments.urls')),
    path('dashboard/', include('dashboard.urls')),
]
