import pytest
from moto import mock_aws
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "name": "Test Product",
    "description": "A great product",
    "category": "electronics",
    "price": 29.99,
    "stock": 10,
    "image_url": "",
}


class TestGetProducts:
    @mock_aws
    def test_empty_catalog(self, dynamodb_table):
        response = client.get("/products")
        assert response.status_code == 200
        assert response.json() == []

    @mock_aws
    def test_returns_products(self, dynamodb_table):
        client.post("/products", json=VALID_PAYLOAD)
        response = client.get("/products")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @mock_aws
    def test_filter_by_category(self, dynamodb_table):
        client.post("/products", json=VALID_PAYLOAD)
        client.post("/products", json={**VALID_PAYLOAD, "name": "Shirt", "category": "clothing"})
        response = client.get("/products?category=electronics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "electronics"

    @mock_aws
    def test_filter_by_price_range(self, dynamodb_table):
        client.post("/products", json={**VALID_PAYLOAD, "price": 10.0})
        client.post("/products", json={**VALID_PAYLOAD, "name": "Expensive", "price": 200.0})
        response = client.get("/products?min_price=5&max_price=50")
        assert response.status_code == 200
        assert all(p["price"] <= 50.0 for p in response.json())

    @mock_aws
    def test_filter_by_available(self, dynamodb_table):
        client.post("/products", json=VALID_PAYLOAD)
        client.post("/products", json={**VALID_PAYLOAD, "name": "Empty", "stock": 0})
        response = client.get("/products?available=true")
        assert response.status_code == 200
        assert all(p["available"] for p in response.json())

    @mock_aws
    def test_invalid_category_returns_400(self, dynamodb_table):
        response = client.get("/products?category=fake_category")
        assert response.status_code == 400


class TestGetProductById:
    @mock_aws
    def test_found(self, dynamodb_table):
        create_resp = client.post("/products", json=VALID_PAYLOAD)
        product_id = create_resp.json()["id"]
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["id"] == product_id

    @mock_aws
    def test_not_found(self, dynamodb_table):
        response = client.get("/products/nonexistent-id")
        assert response.status_code == 404


class TestCreateProduct:
    @mock_aws
    def test_success(self, dynamodb_table):
        response = client.post("/products", json=VALID_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["price"] == 29.99
        assert data["available"] is True
        assert "id" in data

    @mock_aws
    def test_invalid_price_negative(self, dynamodb_table):
        response = client.post("/products", json={**VALID_PAYLOAD, "price": -5})
        assert response.status_code == 422

    @mock_aws
    def test_invalid_price_zero(self, dynamodb_table):
        response = client.post("/products", json={**VALID_PAYLOAD, "price": 0})
        assert response.status_code == 422

    @mock_aws
    def test_negative_stock(self, dynamodb_table):
        response = client.post("/products", json={**VALID_PAYLOAD, "stock": -1})
        assert response.status_code == 422

    @mock_aws
    def test_empty_name(self, dynamodb_table):
        response = client.post("/products", json={**VALID_PAYLOAD, "name": ""})
        assert response.status_code == 422

    @mock_aws
    def test_missing_required_fields(self, dynamodb_table):
        response = client.post("/products", json={"name": "Only name"})
        assert response.status_code == 422

    @mock_aws
    def test_invalid_category(self, dynamodb_table):
        response = client.post("/products", json={**VALID_PAYLOAD, "category": "invalid"})
        assert response.status_code == 400


class TestUpdateProduct:
    @mock_aws
    def test_success(self, dynamodb_table):
        create_resp = client.post("/products", json=VALID_PAYLOAD)
        product_id = create_resp.json()["id"]
        response = client.put(f"/products/{product_id}", json={"name": "Updated"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    @mock_aws
    def test_not_found(self, dynamodb_table):
        response = client.put("/products/nonexistent", json={"name": "X"})
        assert response.status_code == 404

    @mock_aws
    def test_invalid_price(self, dynamodb_table):
        response = client.put("/products/abc", json={"price": -10})
        assert response.status_code == 422

    @mock_aws
    def test_invalid_category(self, dynamodb_table):
        create_resp = client.post("/products", json=VALID_PAYLOAD)
        product_id = create_resp.json()["id"]
        response = client.put(f"/products/{product_id}", json={"category": "invalid"})
        assert response.status_code == 400


class TestUpdateStock:
    @mock_aws
    def test_success(self, dynamodb_table):
        create_resp = client.post("/products", json=VALID_PAYLOAD)
        product_id = create_resp.json()["id"]
        response = client.put(f"/products/{product_id}/stock", json={"stock": 50})
        assert response.status_code == 200
        assert response.json()["stock"] == 50

    @mock_aws
    def test_set_to_zero(self, dynamodb_table):
        create_resp = client.post("/products", json=VALID_PAYLOAD)
        product_id = create_resp.json()["id"]
        response = client.put(f"/products/{product_id}/stock", json={"stock": 0})
        assert response.status_code == 200
        assert response.json()["available"] is False

    @mock_aws
    def test_not_found(self, dynamodb_table):
        response = client.put("/products/nonexistent/stock", json={"stock": 10})
        assert response.status_code == 404

    @mock_aws
    def test_negative_stock(self, dynamodb_table):
        response = client.put("/products/abc/stock", json={"stock": -5})
        assert response.status_code == 422

    @mock_aws
    def test_missing_stock_field(self, dynamodb_table):
        response = client.put("/products/abc/stock", json={})
        assert response.status_code == 422


class TestHealthCheck:
    def test_health(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
