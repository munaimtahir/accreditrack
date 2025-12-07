"""
Views for accounts app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserMeSerializer
from .models import User


class LoginRateThrottle(UserRateThrottle):
    """Custom throttle for login endpoint - stricter rate limiting."""
    rate = '5/minute'


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view that includes user data."""
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            serializer = UserMeSerializer(user)
            response.data['user'] = serializer.data
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me(request):
    """Get current user profile with roles."""
    serializer = UserMeSerializer(request.user)
    return Response(serializer.data)
