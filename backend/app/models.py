import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DECIMAL, Text, TIMESTAMP,
    ForeignKey, Enum, func
)
from sqlalchemy.orm import relationship
from .database import Base


class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"
    delivery = "delivery"


class UnitType(str, enum.Enum):
    kg = "kg"
    piece = "piece"
    kattu = "kattu"


class OrderStatus(str, enum.Enum):
    placed = "placed"
    confirmed = "confirmed"
    packed = "packed"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=True, unique=True)  # optional — collected for delivery contact, not login
    email = Column(String(150), unique=True, nullable=False)  # used for login
    password_hash = Column(String(255), nullable=True)
    address_line = Column(Text, nullable=True)
    locality = Column(String(100), nullable=True)
    latitude = Column(DECIMAL(9, 6), nullable=True)
    longitude = Column(DECIMAL(9, 6), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False)
    name_ta = Column(String(100), nullable=True)
    display_order = Column(Integer, default=0)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name_en = Column(String(150), nullable=False)
    name_ta = Column(String(150), nullable=True)
    unit_type = Column(Enum(UnitType), nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(String(255), nullable=True)
    is_available = Column(Boolean, nullable=False, default=True)
    stock_qty = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    weight_options = relationship("ProductWeightOption", back_populates="product", cascade="all, delete-orphan")


class ProductWeightOption(Base):
    __tablename__ = "product_weight_options"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    grams = Column(Integer, nullable=False)

    product = relationship("Product", back_populates="weight_options")


class DeliveryZone(Base):
    __tablename__ = "delivery_zones"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    delivery_fee = Column(DECIMAL(10, 2), default=0)
    min_order_amt = Column(DECIMAL(10, 2), default=0)
    is_active = Column(Boolean, nullable=False, default=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("delivery_zones.id"), nullable=True)
    delivery_partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.placed)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    delivery_fee = Column(DECIMAL(10, 2), nullable=False, default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(30), nullable=True)
    payment_status = Column(String(20), default="pending")
    delivery_address = Column(Text, nullable=False)
    placed_at = Column(TIMESTAMP, server_default=func.now())
    delivered_at = Column(TIMESTAMP, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_type = Column(Enum(UnitType), nullable=False)
    price_at_order = Column(DECIMAL(10, 2), nullable=False)
    line_total = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")


class OrderStatusLog(Base):
    __tablename__ = "order_status_log"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    changed_at = Column(TIMESTAMP, server_default=func.now())
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class OTPCode(Base):
    """Stores OTP codes for email-based login. In TEST MODE (no email
    credentials configured) the code is returned directly in the API
    response instead of being emailed — see app/auth.py for setup."""
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
