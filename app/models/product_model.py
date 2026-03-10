from datetime import datetime, timezone


def build_product(product_id: str, data: dict) -> dict:
    return {
        "productID": product_id,
        "name": data["name"],
        "description": data.get("description", ""),
        "category": data["category"],
        "price": str(data["price"]),
        "stock": data["stock"],
        "available": data.get("stock", 0) > 0,
        "image_url": data.get("image_url", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def format_product(item: dict) -> dict:
    return {
        "id": item["productID"],
        "name": item["name"],
        "description": item.get("description", ""),
        "category": item["category"],
        "price": float(item["price"]),
        "stock": int(item["stock"]),
        "available": item.get("available", False),
        "image_url": item.get("image_url", ""),
        "created_at": item.get("created_at", ""),
    }
