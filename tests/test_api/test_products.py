import pytest
from fastapi import status


class TestProductsAPI:
    """
    Тесты для API товаров
    """
    
    def test_create_product_success(self, client, admin_token, sample_product_data):
        """
        Тест успешного создания товара
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_product_data["name"]
        assert data["price"] == sample_product_data["price"]
        assert "id" in data
    
    def test_create_product_unauthorized(self, client, sample_product_data):
        """
        Тест создания товара без аутентификации
        """
        response = client.post("/api/v1/products/", json=sample_product_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_products_list(self, client, admin_token, sample_product_data):
        """
        Тест получения списка товаров
        """
        # Сначала создаем товар
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        
        # Получаем список
        response = client.get("/api/v1/products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["products"]) > 0
    
    def test_get_product_by_id(self, client, admin_token, sample_product_data):
        """
        Тест получения товара по ID
        """
        # Создаем товар
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_response = client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        product_id = create_response.json()["id"]
        
        # Получаем товар по ID
        response = client.get(f"/api/v1/products/{product_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == sample_product_data["name"]
    
    def test_get_product_not_found(self, client):
        """
        Тест получения несуществующего товара
        """
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = client.get(f"/api/v1/products/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_product_success(self, client, admin_token, sample_product_data):
        """
        Тест успешного обновления товара
        """
        # Создаем товар
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_response = client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        product_id = create_response.json()["id"]
        
        # Обновляем товар
        update_data = {"name": "Обновленная футболка", "price": 3000}
        response = client.put(f"/api/v1/products/{product_id}", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
    
    def test_update_product_unauthorized(self, client, sample_product_data):
        """
        Тест обновления товара без аутентификации
        """
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = client.put(f"/api/v1/products/{fake_id}", json={"name": "Новое имя"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_product_success(self, client, admin_token, sample_product_data):
        """
        Тест успешного удаления товара
        """
        # Создаем товар
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_response = client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        product_id = create_response.json()["id"]
        
        # Удаляем товар
        response = client.delete(f"/api/v1/products/{product_id}", headers=headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что товар удален
        get_response = client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_search_products(self, client, admin_token, sample_product_data):
        """
        Тест поиска товаров
        """
        # Создаем товар
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        
        # Ищем товар
        response = client.get("/api/v1/products/search/?q=футболка")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["products"]) > 0
        assert any("футболка" in product["name"].lower() for product in data["products"])
    
    def test_get_products_by_size(self, client, admin_token, sample_product_data):
        """
        Тест получения товаров по размеру
        """
        # Создаем товар
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        
        # Получаем товары по размеру
        response = client.get(f"/api/v1/products/size/{sample_product_data['size']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["products"]) > 0
        assert all(product["size"] == sample_product_data["size"] for product in data["products"])
    
    def test_get_products_by_price_range(self, client, admin_token, sample_product_data):
        """
        Тест получения товаров по диапазону цен
        """
        # Создаем товар
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/products/", json=sample_product_data, headers=headers)
        
        # Получаем товары по диапазону цен
        min_price = sample_product_data["price"] - 100
        max_price = sample_product_data["price"] + 100
        
        response = client.get(f"/api/v1/products/price/range?min_price={min_price}&max_price={max_price}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["products"]) > 0
        assert all(min_price <= product["price"] <= max_price for product in data["products"])
    
    def test_invalid_price_range(self, client):
        """
        Тест неверного диапазона цен
        """
        response = client.get("/api/v1/products/price/range?min_price=1000&max_price=500")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Минимальная цена не может быть больше максимальной" in response.json()["detail"]

