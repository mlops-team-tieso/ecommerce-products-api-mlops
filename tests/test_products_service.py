import pytest
from moto import mock_aws
from app.services import products_service as service


VALID_PRODUCT = {
    "name": "Wireless Headphones",
    "description": "Noise-cancelling headphones",
    "category": "electronics",
    "price": 79.99,
    "stock": 50,
    "image_url": "",
}


class TestListProducts:
    @mock_aws
    def test_returns_empty_list(self, dynamodb_table):
        result = service.list_products()
        assert result == []

    @mock_aws
    def test_returns_all_products(self, dynamodb_table):
        service.create_product(VALID_PRODUCT)
        service.create_product({**VALID_PRODUCT, "name": "Keyboard", "price": 120.0})
        result = service.list_products()
        assert len(result) == 2

    @mock_aws
    def test_filter_by_category(self, dynamodb_table):
        service.create_product(VALID_PRODUCT)
        service.create_product({**VALID_PRODUCT, "name": "T-Shirt", "category": "clothing", "price": 19.99})
        result = service.list_products(category="electronics")
        assert len(result) == 1
        assert result[0]["category"] == "electronics"

    @mock_aws
    def test_filter_by_availability(self, dynamodb_table):
        service.create_product(VALID_PRODUCT)
        service.create_product({**VALID_PRODUCT, "name": "Out of Stock Item", "stock": 0})
        result = service.list_products(available=True)
        assert all(p["available"] for p in result)

    @mock_aws
    def test_filter_by_price_range(self, dynamodb_table):
        service.create_product({**VALID_PRODUCT, "price": 10.0})
        service.create_product({**VALID_PRODUCT, "name": "Expensive", "price": 200.0})
        result = service.list_products(min_price=5.0, max_price=50.0)
        assert all(p["price"] <= 50.0 for p in result)

    def test_invalid_category_raises_error(self, dynamodb_table):
        with pytest.raises(ValueError, match="Invalid category"):
            service.list_products(category="nonexistent_category")


class TestGetProduct:
    @mock_aws
    def test_found(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        result = service.get_product(created["id"])
        assert result is not None
        assert result["name"] == "Wireless Headphones"
        assert result["price"] == 79.99

    @mock_aws
    def test_not_found(self, dynamodb_table):
        result = service.get_product("nonexistent-id")
        assert result is None


class TestCreateProduct:
    @mock_aws
    def test_success(self, dynamodb_table):
        result = service.create_product(VALID_PRODUCT)
        assert result["name"] == "Wireless Headphones"
        assert result["price"] == 79.99
        assert result["stock"] == 50
        assert result["available"] is True
        assert "id" in result
        assert "created_at" in result

    @mock_aws
    def test_zero_stock_sets_unavailable(self, dynamodb_table):
        data = {**VALID_PRODUCT, "stock": 0}
        result = service.create_product(data)
        assert result["available"] is False

    def test_invalid_category(self, dynamodb_table):
        data = {**VALID_PRODUCT, "category": "invalid_category"}
        with pytest.raises(ValueError, match="Invalid category"):
            service.create_product(data)

    @mock_aws
    def test_product_persists_in_db(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        fetched = service.get_product(created["id"])
        assert fetched["name"] == created["name"]
        assert fetched["price"] == created["price"]


class TestUpdateProduct:
    @mock_aws
    def test_update_name(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        result = service.update_product(created["id"], {"name": "Updated Name"})
        assert result["name"] == "Updated Name"

    @mock_aws
    def test_update_price(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        result = service.update_product(created["id"], {"price": 99.99})
        assert result["price"] == 99.99

    @mock_aws
    def test_update_stock_sets_availability(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        result = service.update_product(created["id"], {"stock": 0})
        assert result["stock"] == 0
        assert result["available"] is False

    @mock_aws
    def test_not_found(self, dynamodb_table):
        result = service.update_product("nonexistent", {"name": "X"})
        assert result is None

    @mock_aws
    def test_invalid_category_with_existing_product(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        with pytest.raises(ValueError, match="Invalid category"):
            service.update_product(created["id"], {"category": "invalid"})

    @mock_aws
    def test_skips_none_values(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        result = service.update_product(created["id"], {"name": "New", "description": None})
        assert result["name"] == "New"
        assert result["description"] == "Noise-cancelling headphones"


class TestUpdateStock:
    @mock_aws
    def test_success(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        result = service.update_stock(created["id"], 100)
        assert result["stock"] == 100
        assert result["available"] is True

    @mock_aws
    def test_set_to_zero(self, dynamodb_table):
        created = service.create_product(VALID_PRODUCT)
        result = service.update_stock(created["id"], 0)
        assert result["stock"] == 0
        assert result["available"] is False

    @mock_aws
    def test_not_found(self, dynamodb_table):
        result = service.update_stock("nonexistent", 10)
        assert result is None
