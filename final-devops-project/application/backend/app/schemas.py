from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sku: str = Field(min_length=1, max_length=40)
    category: str = Field(default="General", min_length=1, max_length=60)
    quantity: int = Field(default=0, ge=0)
    price: float = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    """Every field is optional, so a client can change just one value."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    sku: str | None = Field(default=None, min_length=1, max_length=40)
    category: str | None = Field(default=None, min_length=1, max_length=60)
    quantity: int | None = Field(default=None, ge=0)
    price: float | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)


class StockAdjustment(BaseModel):
    change: int = Field(description="Positive to receive stock, negative to ship it")


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    low_stock: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Stats(BaseModel):
    total_products: int
    total_units: int
    inventory_value: float
    low_stock_count: int
    categories: int
