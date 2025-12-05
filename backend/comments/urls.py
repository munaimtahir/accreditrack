"""
URLs for comments app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet

router = DefaultRouter()
router.register(r'', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]

# For nested routes from item-status
urlpatterns_nested = [
    path('', CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list-create'),
]
