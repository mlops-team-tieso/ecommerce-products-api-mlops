from app.models.product_model import build_product, format_product


class TestBuildProduct:
    def test_creates_full_product(self):
        data = {
            "name": "Test",
            "description": "Desc",
            "category": "electronics",
            "price": 25.0,
            "stock": 10,
            "image_url": "http://img.com/test.png",
        }
        result = build_product("id-1", data)
        assert result["id"] == "id-1"
        assert result["name"] == "Test"
        assert result["price"] == "25.0"
        assert result["stock"] == 10
        assert result["available"] is True
        assert result["created_at"] is not None

    def test_zero_stock_is_unavailable(self):
        data = {"name": "Empty", "category": "books", "price": 5.0, "stock": 0}
        result = build_product("id-2", data)
        assert result["available"] is False

    def test_defaults_for_optional_fields(self):
        data = {"name": "Min", "category": "toys", "price": 1.0, "stock": 1}
        result = build_product("id-3", data)
        assert result["description"] == ""
        assert result["image_url"] == ""


class TestFormatProduct:
    def test_converts_types_correctly(self):
        item = {
            "id": "id-1",
            "name": "Test",
            "description": "Desc",
            "category": "electronics",
            "price": "25.0",
            "stock": 10,
            "available": True,
            "image_url": "",
            "created_at": "2025-01-01T00:00:00",
        }
        result = format_product(item)
        assert isinstance(result["price"], float)
        assert result["price"] == 25.0
        assert isinstance(result["stock"], int)

    def test_handles_missing_optional_fields(self):
        item = {"id": "id-1", "name": "Test", "category": "electronics", "price": "10", "stock": 0}
        result = format_product(item)
        assert result["description"] == ""
        assert result["available"] is False
        assert result["image_url"] == ""
        assert result["created_at"] == ""
