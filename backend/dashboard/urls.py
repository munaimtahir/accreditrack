"""
URLs for dashboard app.
"""
from django.urls import path
from .views import (
    dashboard_summary,
    pending_items,
    modules_list,
    module_dashboard,
    user_assignments
)

urlpatterns = [
    path('summary/', dashboard_summary, name='dashboard-summary'),
    path('pending-items/', pending_items, name='dashboard-pending-items'),
    path('modules/', modules_list, name='modules-list'),
    path('modules/<uuid:module_id>/', module_dashboard, name='module-dashboard'),
    path('user-assignments/', user_assignments, name='user-assignments'),
]
