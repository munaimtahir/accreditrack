"""
URLs for dashboard app.
"""
from django.urls import path
from .views import dashboard_summary, pending_items

urlpatterns = [
    path('summary/', dashboard_summary, name='dashboard-summary'),
    path('pending-items/', pending_items, name='dashboard-pending-items'),
]
