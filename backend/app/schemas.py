from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .models import UnitType, OrderStatus, UserRole


# ---------- Products ----------
class WeightOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    grams: int


class ProductBase(BaseModel):
    name_en: str
    name_ta: Optional[str] = None
    unit_type: UnitType
    price_per_unit: Decimal
    image_url: Optional[str] = None
    is_available: bool = True
    stock_qty: Optional[Decimal] = None
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    weight_options_grams: Optional[List[int]] = None  # e.g. [250, 500, 750, 1000]


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    weight_options: List[WeightOptionOut] = []


# ---------- Orders ----------
class OrderItemIn(BaseModel):
    product_id: int
    quantity: Decimal
    unit_type: UnitType


class OrderCreate(BaseModel):
    customer_id: int
    zone_id: Optional[int] = None
    delivery_address: str
    payment_method: Optional[str] = "cod"
    items: List[OrderItemIn]


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    quantity: Decimal
    unit_type: UnitType
    price_at_order: Decimal
    line_total: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    status: OrderStatus
    subtotal: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_method: Optional[str]
    payment_status: Optional[str]
    delivery_address: str
    placed_at: datetime
    items: List[OrderItemOut] = []


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    changed_by: Optional[int] = None


# ---------- Auth ----------
class RequestOTP(BaseModel):
    email: str


class RequestOTPOut(BaseModel):
    message: str
    # TEST MODE ONLY: present when no real email is configured (see
    # app/auth.py). Once EMAIL_ADDRESS/EMAIL_APP_PASSWORD are set, this
    # will be None and the code only goes out by real email.
    debug_otp: Optional[str] = None


class VerifyOTP(BaseModel):
    email: str
    code: str
    name: Optional[str] = None  # used to create the profile on first login
    phone: Optional[str] = None  # optional contact number, for delivery


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


# ---------- Users ----------
class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: UserRole = UserRole.customer
    address_line: Optional[str] = None
    locality: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    locality: Optional[str] = None
