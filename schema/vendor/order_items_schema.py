from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Pydantic model for individual order items
class OrderItemSchema(BaseModel):
    item_id: str
    item_name: str
    item_price: float
    quantity: int
    total_price: float
    product_image: Optional[str] = None

    # Add from_attributes=True to allow from_orm
    class Config:
        orm_mode = True
        from_attributes = True


# Pydantic model for order response, which includes a list of order items
class OrderResponseSchema(BaseModel):
    id: str
    customer_id: str
    total_amount: float
    address: str
    city: str
    state: str
    payment_method: str
    payment_status: str
    is_paid: bool
    status: str
    created_datetime: datetime
    updated_datetime: datetime
    items: List[OrderItemSchema] = []

    # Add from_attributes=True to allow from_orm
    class Config:
        orm_mode = True
        from_attributes = True
