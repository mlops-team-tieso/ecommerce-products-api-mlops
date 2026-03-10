from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    StockUpdate,
    ProductResponse,
)
from app.services import products_service as service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
):
    try:
        return service.list_products(
            category=category,
            min_price=min_price,
            max_price=max_price,
            available=available,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID):
    product = service.get_product(str(product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate):
    try:
        return service.create_product(payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: UUID, payload: ProductUpdate):
    try:
        product = service.update_product(
            str(product_id), payload.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}/stock", response_model=ProductResponse)
def update_stock(product_id: UUID, payload: StockUpdate):
    product = service.update_stock(str(product_id), payload.stock)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
