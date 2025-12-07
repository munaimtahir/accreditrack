"""
Tests for health check endpoint.
"""
import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_check():
    """Test health check endpoint returns 200 OK."""
    client = Client()
    response = client.get('/health/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.django_db
def test_health_check_method_not_allowed():
    """Test health check endpoint only accepts GET."""
    client = Client()
    response = client.post('/health/')
    assert response.status_code == 405  # Method Not Allowed
