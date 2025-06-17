from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import datetime

# === Cart Item Request ===
class CartItemRequest(BaseModel):
    item_id: str
    quantity: int

# === Add to Cart Request ===
class AddToCartRequest(BaseModel):
    customer_id: Optional[str]  # Registered user
    guest_user_id: Optional[str]  # Guest user
    cart_id: Optional[str]       # Anonymous user cart identifier
    items: List[CartItemRequest]

    @model_validator(mode="after")
    def check_identifiers(self) -> 'AddToCartRequest':
        if not (self.customer_id or self.guest_user_id or self.cart_id):
            raise ValueError("At least one of customer_id, guest_user_id, or cart_id must be provided.")
        return self


# === Cart Item Response ===
class CartItemResponse(BaseModel):
    item_id: str
    item_name: str
    item_price: float
    mrp_price: float                # ← Add this
    cart_discount: float
    quantity: int
    total_price: float
    product_image: Optional[str]

# === Cart Response ===
class CartResponse(BaseModel):
    cart_id: str
    customer_id: Optional[str]
    guest_user_id: Optional[str]
    items: List[CartItemResponse]
    mrp_price: float                # ← Add this
    cart_discount: float
    total_cart_price: float
    created_datetime: datetime
    updated_datetime: datetime

# === Update Cart Item Request ===
class UpdateCartItemRequest(BaseModel):
    cart_id: Optional[str]
    customer_id: Optional[str]
    guest_user_id: Optional[str]
    item_id: str
    quantity: int

    @model_validator(mode="after")
    def check_identifiers(self) -> 'UpdateCartItemRequest':
        if not (self.customer_id or self.guest_user_id or self.cart_id):
            raise ValueError("At least one of customer_id, guest_user_id, or cart_id must be provided.")
        return self
    
class MergeCartRequest(BaseModel):
    temp_cart_id: str  # The anonymous cart ID created before login
    customer_id: Optional[str] = None
    guest_user_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_identifiers(self) -> 'MergeCartRequest':
        if not (self.customer_id or self.guest_user_id):
            raise ValueError("Either customer_id or guest_user_id must be provided for cart merge.")
        return self

# === Remove Cart Item Request ===
class RemoveCartItemRequest(BaseModel):
    cart_id: Optional[str]
    customer_id: Optional[str]
    guest_user_id: Optional[str]
    item_id: str

    @model_validator(mode="after")
    def check_identifiers(self) -> 'RemoveCartItemRequest':
        if not (self.customer_id or self.guest_user_id or self.cart_id):
            raise ValueError("At least one of customer_id, guest_user_id, or cart_id must be provided.")
        return self


class UpdateCartQuantityRequest(BaseModel):
    cart_id: Optional[str]
    customer_id: Optional[str]
    guest_user_id: Optional[str]
    item_id: str
    new_quantity: int

    @model_validator(mode="after")
    def check_identifiers(self) -> 'UpdateCartQuantityRequest':
        if not (self.customer_id or self.guest_user_id or self.cart_id):
            raise ValueError("At least one of customer_id, guest_user_id, or cart_id must be provided.")
        return self
    
    
class UpdateCartQuantityRequest(BaseModel):
    cart_id: str
    item_id: str
    quantity: int