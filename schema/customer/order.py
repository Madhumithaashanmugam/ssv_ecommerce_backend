from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime
from pydantic import ConfigDict


class OrderStatus(str, Enum):
    pending = "Pending"
    accepted = "Accepted"
    declined = "Declined"
    completed = "Completed"
    returned = "Returned"


class PaymentMethod(str, Enum):
    online = "Online"
    cod = "Cash On Delivery"


class PaymentStatus(str, Enum):
    pending = "Pending"
    success = "Success"
    failed = "Failed"


class OrderItemInput(BaseModel):
    item_id: str
    item_name: str
    item_price: float
    mrp_price: float
    discount: float  # base discount (e.g., 10%)
    additional_discount: float  # extra discount (e.g., for bulk)
    quantity: int
    unit_price: float
    product_image: Optional[str]
    note: Optional[str] = None



class OrderItem(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    unit_price: float
    total_price: float  # MRP × Quantity
    discount: float
    additional_discount: float
    product_image: Optional[str]
    note: Optional[str] = None



class CreateOrderRequest(BaseModel):
    user_id: Optional[str] = None
    guest_user_id: Optional[str] = None
    items: List[OrderItemInput]
    payment_method: PaymentMethod
    address: str
    city: str
    state: str
    total_mrp: Optional[float] = None
    total_discount_amount: Optional[float] = None
    total_payable: Optional[float] = None
    effective_discount_percent: Optional[float] = None

class UpdateOrderStatusRequest(BaseModel):
    order_status: OrderStatus
    
class OrderQueryRequest(BaseModel):
    user_id: Optional[str] = None
    guest_user_id: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    user_id: Optional[str]
    guest_user_id: Optional[str]
    total_price: float
    items: List[OrderItem]
    order_status: OrderStatus
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    is_paid: bool
    reason: Optional[str] = None

    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str]
    razorpay_signature: Optional[str]

    address: str
    city: str
    state: str

    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)

   
class OrderReasonUpdate(BaseModel):
    order_id: str
    reason: str

class OrderQueryRequest(BaseModel):
    user_id: Optional[str] = None
    guest_user_id: Optional[str] = None
    
    
    class Config:
        from_attributes = True
