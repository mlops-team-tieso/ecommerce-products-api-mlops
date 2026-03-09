from pydantic import BaseModel, Field
from typing import Optional


VALID_CATEGORIES = [
    "electronics",
    "clothing",
    "home",
    "sports",
    "books",
    "toys",
    "food",
    "beauty",
    "automotive",
    "garden",
]


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    category: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    image_url: str = Field(default="")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None


class StockUpdate(BaseModel):
    stock: int = Field(..., ge=0)


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price: float
    stock: int
    available: bool
    image_url: str
    created_at: str
