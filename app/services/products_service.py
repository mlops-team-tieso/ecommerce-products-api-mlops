import uuid
from app.repo import products_repositories as repo
from app.models.product_model import build_product, format_product
from app.schemas.product_schema import VALID_CATEGORIES


def list_products(category=None, min_price=None, max_price=None, available=None):
    if category and category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category. Valid categories: {VALID_CATEGORIES}")

    items = repo.get_all(
        category=category,
        min_price=min_price,
        max_price=max_price,
        available=available,
    )
    return [format_product(item) for item in items]


def get_product(product_id: str):
    item = repo.get_by_id(product_id)
    if not item:
        return None
    return format_product(item)


def create_product(data: dict):
    if data.get("category") and data["category"] not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category. Valid categories: {VALID_CATEGORIES}")

    product_id = str(uuid.uuid4())
    product = build_product(product_id, data)
    repo.create(product)
    return format_product(product)


def update_product(product_id: str, data: dict):
    existing = repo.get_by_id(product_id)
    if not existing:
        return None

    if data.get("category") and data["category"] not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category. Valid categories: {VALID_CATEGORIES}")

    update_data = {}
    for key, value in data.items():
        if value is not None:
            if key == "price":
                update_data[key] = str(value)
            else:
                update_data[key] = value

    if "stock" in update_data:
        update_data["available"] = update_data["stock"] > 0

    updated = repo.update(product_id, update_data)
    return format_product(updated)


def update_stock(product_id: str, stock: int):
    existing = repo.get_by_id(product_id)
    if not existing:
        return None

    updated = repo.update_stock(product_id, stock)
    return format_product(updated)
