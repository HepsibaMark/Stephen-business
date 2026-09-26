from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.OrderOut, status_code=201)
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Customer app calls this on checkout. Prices are snapshotted from the
    current product price so later price changes never affect old orders."""

    zone = None
    delivery_fee = Decimal("0")
    if payload.zone_id:
        zone = db.query(models.DeliveryZone).filter(models.DeliveryZone.id == payload.zone_id).first()
        if zone:
            delivery_fee = zone.delivery_fee

    order = models.Order(
        customer_id=payload.customer_id,
        zone_id=payload.zone_id,
        delivery_address=payload.delivery_address,
        payment_method=payload.payment_method,
        subtotal=Decimal("0"),
        delivery_fee=delivery_fee,
        total_amount=Decimal("0"),
    )
    db.add(order)
    db.flush()

    subtotal = Decimal("0")
    for item in payload.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product or not product.is_available:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} unavailable")

        # price_per_unit is per kg/piece/kattu — quantity is in the same unit
        line_total = (product.price_per_unit * item.quantity).quantize(Decimal("0.01"))
        subtotal += line_total

        db.add(models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_type=item.unit_type,
            price_at_order=product.price_per_unit,
            line_total=line_total,
        ))

    order.subtotal = subtotal
    order.total_amount = subtotal + delivery_fee

    db.add(models.OrderStatusLog(order_id=order.id, status=models.OrderStatus.placed))
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(models.Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/", response_model=List[schemas.OrderOut])
def list_orders(
    customer_id: Optional[int] = None,
    delivery_partner_id: Optional[int] = None,
    status: Optional[models.OrderStatus] = None,
    db: Session = Depends(get_db),
):
    """Used by: customer order history, delivery partner's assigned-orders list,
    and admin's order queue — filter by whichever ID/status is relevant."""
    query = db.query(models.Order).options(joinedload(models.Order.items))
    if customer_id is not None:
        query = query.filter(models.Order.customer_id == customer_id)
    if delivery_partner_id is not None:
        query = query.filter(models.Order.delivery_partner_id == delivery_partner_id)
    if status is not None:
        query = query.filter(models.Order.status == status)
    return query.order_by(models.Order.placed_at.desc()).all()


@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(order_id: int, payload: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    """Admin marks confirmed/packed; delivery partner marks out_for_delivery/delivered."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    db.add(models.OrderStatusLog(
        order_id=order.id,
        status=payload.status,
        changed_by=payload.changed_by,
    ))
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/assign", response_model=schemas.OrderOut)
def assign_delivery_partner(order_id: int, delivery_partner_id: int, db: Session = Depends(get_db)):
    """Admin assigns a delivery partner to an order."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.delivery_partner_id = delivery_partner_id
    db.commit()
    db.refresh(order)
    return order
