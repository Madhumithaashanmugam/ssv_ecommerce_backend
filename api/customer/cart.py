from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from models.customer.cart import Cart
from typing import Optional
from uuid import uuid4

from config.db.session import get_db
from schema.customer.cart_schema import (
    AddToCartRequest,
    CartResponse,
    UpdateCartItemRequest,
    CartItemResponse,
    RemoveCartItemRequest,
    UpdateCartQuantityRequest,
    MergeCartRequest
)
from service.customer.cart import (
    add_items_to_cart,
    update_cart_item,
    remove_cart_item,
    get_cart_items, 
    update_cart_item_quantity,
    delete_cart_by_id,
    merge_carts
    
    
)

cart_router = APIRouter(prefix="/cart", tags=["Cart"])
from fastapi import Request

@cart_router.post("/add", response_model=CartResponse)
async def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db)):
    return add_items_to_cart(request, db)


@cart_router.delete("/remove")
def remove_item_from_cart(
    request: RemoveCartItemRequest = Body(...),
    db: Session = Depends(get_db)
):
    return remove_cart_item(request, db)


@cart_router.get("/get", response_model=CartResponse)
def get_customer_cart(
    db: Session = Depends(get_db),
    customer_id: Optional[str] = Query(default=None),
    guest_user_id: Optional[str] = Query(default=None),
    cart_id: Optional[str] = Query(default=None)
):
    return get_cart_items(
        db=db,
        customer_id=customer_id,
        guest_user_id=guest_user_id,
        cart_id=cart_id
    )


@cart_router.post("/api/cart/create")
def create_cart(db: Session = Depends(get_db)):
    cart_id = uuid4().hex
    new_cart = Cart(cart_id=cart_id, guest_user_id=None)  # or however you handle guest users
    db.add(new_cart)
    db.commit()
    return {"cart_id": cart_id}

@cart_router.put("/update-quantity", response_model=CartResponse)
def update_cart_quantity(
    payload: UpdateCartQuantityRequest,
    db: Session = Depends(get_db)
):
    return update_cart_item_quantity(
        cart_id=payload.cart_id,
        item_id=payload.item_id,
        quantity=payload.quantity,
        db=db
    )
    
@cart_router.delete("/cart/{cart_id}")
def delete_cart(cart_id: str, db: Session = Depends(get_db)):
    return delete_cart_by_id(cart_id, db)

@cart_router.post("/cart/merge", response_model=CartResponse)
def merge_cart_api(request: MergeCartRequest, db: Session = Depends(get_db)):
    return merge_carts(request, db)
