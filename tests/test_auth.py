import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient, test_user):
    """Test user registration"""
    response = client.post("/api/v1/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert "user_id" in data
    assert "created_at" in data


def test_register_duplicate_user(client: TestClient, test_user):
    """Test registration with duplicate username"""
    # Register first time
    client.post("/api/v1/register", json=test_user)
    
    # Try to register again
    response = client.post("/api/v1/register", json=test_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_user(client: TestClient, test_user):
    """Test user login"""
    # Register user first
    client.post("/api/v1/register", json=test_user)
    
    # Login
    response = client.post("/api/v1/login", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post("/api/v1/login", json={
        "username": "nonexistent",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_current_user(client: TestClient, test_user):
    """Test getting current user info"""
    # Register and login
    client.post("/api/v1/register", json=test_user)
    login_response = client.post("/api/v1/login", json=test_user)
    token = login_response.json()["access_token"]
    
    # Get user info
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]


def test_search_users(client: TestClient, test_user):
    """Test user search"""
    # Register test user
    client.post("/api/v1/register", json=test_user)
    login_response = client.post("/api/v1/login", json=test_user)
    token = login_response.json()["access_token"]
    
    # Register another user
    client.post("/api/v1/register", json={
        "username": "anotheruser",
        "password": "password123"
    })
    
    # Search users
    response = client.get(
        "/api/v1/users?username=another",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["username"] == "anotheruser"