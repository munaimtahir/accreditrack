"""
URLs for item status endpoints.
"""
from django.urls import path, include
from .views import ItemStatusViewSet
from evidence.views import EvidenceViewSet
from comments.views import CommentViewSet

urlpatterns = [
    path('<uuid:pk>/', ItemStatusViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='item-status-detail'),
    path('<uuid:item_status_id>/evidence/', EvidenceViewSet.as_view({'get': 'list', 'post': 'create'}), name='item-status-evidence'),
    path('<uuid:item_status_id>/comments/', CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='item-status-comments'),
]