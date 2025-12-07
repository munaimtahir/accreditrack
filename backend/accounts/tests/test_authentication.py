"""
Tests for authentication endpoints.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.mark.django_db
def test_login_success(api_client, test_user):
    """Test successful login returns tokens and user data."""
    response = api_client.post('/api/v1/auth/login/', {
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert 'user' in response.data
    assert response.data['user']['email'] == 'test@example.com'


@pytest.mark.django_db
def test_login_invalid_credentials(api_client, test_user):
    """Test login with invalid credentials returns 401."""
    response = api_client.post('/api/v1/auth/login/', {
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_login_nonexistent_user(api_client):
    """Test login with nonexistent user returns 401."""
    response = api_client.post('/api/v1/auth/login/', {
        'email': 'nonexistent@example.com',
        'password': 'password123'
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_me_requires_authentication(api_client):
    """Test /users/me/ endpoint requires authentication."""
    response = api_client.get('/api/v1/users/me/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_me_authenticated(api_client, test_user):
    """Test /users/me/ endpoint returns user data when authenticated."""
    # Login first
    login_response = api_client.post('/api/v1/auth/login/', {
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    token = login_response.data['access']
    
    # Use token to access /users/me/
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.get('/api/v1/users/me/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'test@example.com'


@pytest.mark.django_db
def test_token_refresh(api_client, test_user):
    """Test token refresh endpoint."""
    # Login first
    login_response = api_client.post('/api/v1/auth/login/', {
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    refresh_token = login_response.data['refresh']
    
    # Refresh token
    response = api_client.post('/api/v1/auth/refresh/', {
        'refresh': refresh_token
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
