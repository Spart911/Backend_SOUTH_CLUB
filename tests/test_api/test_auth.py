import pytest
from fastapi import status


class TestAuthAPI:
    """
    Тесты для API аутентификации
    """
    
    def test_admin_login_success(self, client, admin_credentials):
        """
        Тест успешного входа админа
        """
        response = client.post("/api/v1/auth/login-json", json=admin_credentials)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_admin_login_invalid_credentials(self, client):
        """
        Тест входа с неверными учетными данными
        """
        invalid_credentials = {
            "username": "wrong_user",
            "password": "wrong_password"
        }
        
        response = client.post("/api/v1/auth/login-json", json=invalid_credentials)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Неверные учетные данные" in response.json()["detail"]
    
    def test_admin_login_missing_fields(self, client):
        """
        Тест входа с отсутствующими полями
        """
        incomplete_credentials = {"username": "admin"}
        
        response = client.post("/api/v1/auth/login-json", json=incomplete_credentials)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_admin_login_form_data(self, client, admin_credentials):
        """
        Тест входа через form-data
        """
        response = client.post(
            "/api/v1/auth/login",
            data=admin_credentials
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_admin_login_empty_request(self, client):
        """
        Тест входа с пустым запросом
        """
        response = client.post("/api/v1/auth/login-json", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

