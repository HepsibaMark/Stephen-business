from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[schemas.ProductOut])
def list_products(
    available_only: bool = True,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Catalog listing — what the customer app's browse/quick-list screens call."""
    query = db.query(models.Product)
    if available_only:
        query = query.filter(models.Product.is_available == True)  # noqa: E712
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)
    return query.order_by(models.Product.id).all()


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=schemas.ProductOut, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Admin panel uses this to add a new item to the catalog."""
    data = payload.model_dump(exclude={"weight_options_grams"})
    product = models.Product(**data)
    db.add(product)
    db.flush()  # get product.id before adding weight options

    if payload.weight_options_grams:
        for grams in payload.weight_options_grams:
            db.add(models.ProductWeightOption(product_id=product.id, grams=grams))

    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, payload: schemas.ProductBase, db: Session = Depends(get_db)):
    """Admin panel uses this for price updates / marking out-of-stock."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in payload.model_dump().items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
