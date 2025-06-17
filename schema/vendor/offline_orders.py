from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class OrderItem(BaseModel):
    item_id: str
    quantity: int

    class Config:
        orm_mode = True


class OfflineOrderBase(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    order_date: date
    delivery_date: Optional[date] = None
    payment_status: str  # "Paid", "Unpaid", "Partial"
    payment_method: str  # "Cash", "Bank Transfer", "UPI"
    total_amount: Optional[float] = None  # Make optional
    discount: Optional[float] = None      # Make optional
    amount_paid: Optional[float] = 0.0
    balance_due: Optional[float] = None   # Make optional
    created_by: str
    notes: Optional[str] = None
    items: List[OrderItem]

    class Config:
        orm_mode = True


class OfflineOrderCreate(OfflineOrderBase):
    pass


class OfflineOrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    delivery_date: Optional[date] = None
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    total_amount: Optional[float] = None
    discount: Optional[float] = None
    amount_paid: Optional[float] = None
    balance_due: Optional[float] = None
    notes: Optional[str] = None
    items: Optional[List[OrderItem]] = None

    class Config:
        orm_mode = True

class UpdateOrderReturnStatus(BaseModel):
    order_id: str  
    is_returned: bool

class OfflineOrderResponse(OfflineOrderBase):
    id: str
    created_datetime: datetime
    updated_datetime: datetime

    class Config:
        orm_mode = True
