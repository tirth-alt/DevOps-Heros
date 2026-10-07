import logging

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Response, status
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Product
from app.schemas import ProductCreate, ProductOut, ProductUpdate, Stats, StockAdjustment

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("stockwise")

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Exposes request count, latency and error metrics at /metrics for Prometheus
Instrumentator().instrument(app).expose(app, include_in_schema=False)


def to_out(product: Product) -> ProductOut:
    return ProductOut(
        id=product.id,
        name=product.name,
        sku=product.sku,
        category=product.category,
        quantity=product.quantity,
        price=float(product.price),
        reorder_level=product.reorder_level,
        low_stock=product.quantity <= product.reorder_level,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


# ---------------------------------------------------------------- health
@app.get("/", tags=["info"])
def root():
    return {"app": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["health"])
def health():
    """Liveness: the process is running. Does not touch the database."""
    return {"status": "UP"}


@app.get("/ready", tags=["health"])
def ready(db: Session = Depends(get_db)):
    """Readiness: the database is reachable, so the app can serve traffic."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - only hit when the DB is down
        log.error("Readiness check failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database not reachable") from exc
    return {"status": "READY"}


# ---------------------------------------------------------------- products API
api = APIRouter(prefix="/api", tags=["products"])


@api.get("/products", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None, description="Search name or SKU"),
    category: str | None = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(Product).order_by(Product.name)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.sku.ilike(like)))
    if category:
        stmt = stmt.where(Product.category == category)
    if low_stock:
        stmt = stmt.where(Product.quantity <= Product.reorder_level)
    return [to_out(p) for p in db.scalars(stmt).all()]


@api.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"SKU '{payload.sku}' already exists") from exc
    db.refresh(product)
    log.info("Created product id=%s sku=%s", product.id, product.sku)
    return to_out(product)


@api.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return to_out(get_product_or_404(db, product_id))


@api.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU already exists") from exc
    db.refresh(product)
    log.info("Updated product id=%s", product.id)
    return to_out(product)


@api.patch("/products/{product_id}/stock", response_model=ProductOut)
def adjust_stock(product_id: int, payload: StockAdjustment, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    new_quantity = product.quantity + payload.change
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail=f"Only {product.quantity} units in stock")
    product.quantity = new_quantity
    db.commit()
    db.refresh(product)
    log.info("Stock for id=%s changed by %s to %s", product.id, payload.change, product.quantity)
    return to_out(product)


@api.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    db.delete(product)
    db.commit()
    log.info("Deleted product id=%s", product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.get("/stats", response_model=Stats)
def stats(db: Session = Depends(get_db)):
    total_products, total_units, inventory_value, categories = db.execute(
        select(
            func.count(Product.id),
            func.coalesce(func.sum(Product.quantity), 0),
            func.coalesce(func.sum(Product.quantity * Product.price), 0),
            func.count(func.distinct(Product.category)),
        )
    ).one()
    low_stock_count = db.scalar(
        select(func.count(Product.id)).where(Product.quantity <= Product.reorder_level)
    )
    return Stats(
        total_products=total_products,
        total_units=int(total_units),
        inventory_value=round(float(inventory_value), 2),
        low_stock_count=low_stock_count or 0,
        categories=categories,
    )


app.include_router(api)
