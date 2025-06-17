import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.customer.cart import Cart
from models.vendor.items import Item
from datetime import datetime
from schema.customer.cart_schema import AddToCartRequest, CartResponse, CartItemResponse, MergeCartRequest
from models.customer.user import User as CustomerUser
from models.customer.guest_user import GuestUser
from schema.customer.cart_schema import UpdateCartItemRequest
from schema.customer.cart_schema import RemoveCartItemRequest
from typing import Optional


from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid



def add_items_to_cart(request: AddToCartRequest, db: Session) -> CartResponse:
    cart_items_response = []
    total_cart_mrp = 0.0
    total_cart_discount = 0.0
    total_cart_price = 0.0

    filters = []
    if request.customer_id:
        filters.append(Cart.customer_id == request.customer_id)
    if request.guest_user_id:
        filters.append(Cart.guest_user_id == request.guest_user_id)
    if request.cart_id:
        filters.append(Cart.cart_id == request.cart_id)

    existing_cart_items = db.query(Cart).filter(*filters).all() if filters else []
    cart_id = existing_cart_items[0].cart_id if existing_cart_items else (request.cart_id or str(uuid.uuid4()))

    if request.customer_id:
        customer = db.query(CustomerUser).filter(CustomerUser.id == request.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

    for item_req in request.items:
        item = db.query(Item).filter(Item.id == item_req.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_req.item_id} not found")

        item_mrp = item.item_price
        base_discount = item.discount or 0.0
        quantity = item_req.quantity

        bulk_discount = 10.0 if quantity > 5 else 0.0
        compounded_factor = (1 - base_discount / 100) * (1 - bulk_discount / 100)
        compounded_discount = round((1 - compounded_factor) * 100, 2)

        final_price_per_unit = round(item_mrp * compounded_factor, 2)
        final_total_price = round(final_price_per_unit * quantity, 2)

        item_filters = [
            Cart.cart_id == cart_id,
            Cart.item_id == item.id
        ]
        if request.customer_id:
            item_filters.append(Cart.customer_id == request.customer_id)
        if request.guest_user_id:
            item_filters.append(Cart.guest_user_id == request.guest_user_id)

        cart_entry = db.query(Cart).filter(*item_filters).first()

        if cart_entry:
            cart_entry.quantity += quantity
            updated_quantity = cart_entry.quantity

            bulk_discount = 10.0 if updated_quantity > 5 else 0.0
            compounded_factor = (1 - base_discount / 100) * (1 - bulk_discount / 100)
            compounded_discount = round((1 - compounded_factor) * 100, 2)

            final_price_per_unit = round(item_mrp * compounded_factor, 2)
            final_total_price = round(final_price_per_unit * updated_quantity, 2)

            cart_entry.discount = compounded_discount
            cart_entry.final_price = final_price_per_unit
            cart_entry.total_price = final_total_price
            cart_entry.updated_datetime = datetime.utcnow()
        else:
            cart_entry = Cart(
                cart_id=cart_id,
                customer_id=request.customer_id,
                guest_user_id=request.guest_user_id,
                item_id=item.id,
                quantity=quantity,
                mrp_price=item_mrp,
                discount=compounded_discount,
                final_price=final_price_per_unit,
                total_price=final_total_price,
                created_datetime=datetime.utcnow(),
                updated_datetime=datetime.utcnow()
            )
            db.add(cart_entry)

        db.commit()
        db.refresh(cart_entry)

        cart_items_response.append(CartItemResponse(
            item_id=item.id,
            item_name=item.item_name,
            item_price=final_price_per_unit,
            mrp_price=item_mrp,
            cart_discount=compounded_discount,
            quantity=cart_entry.quantity,
            total_price=round(final_price_per_unit * cart_entry.quantity, 2),
            product_image=item.product_image
        ))

    # Recalculate totals
    all_items = db.query(Cart).filter(Cart.cart_id == cart_id).all()
    for entry in all_items:
        total_cart_mrp += entry.mrp_price * entry.quantity
        total_cart_discount += (entry.mrp_price * entry.quantity) - entry.total_price
        total_cart_price += entry.total_price

    created_time = all_items[0].created_datetime if all_items else datetime.utcnow()
    updated_time = all_items[-1].updated_datetime if all_items else datetime.utcnow()

    return CartResponse(
        cart_id=cart_id,
        customer_id=request.customer_id,
        guest_user_id=request.guest_user_id,
        items=cart_items_response,
        mrp_price=round(total_cart_mrp, 2),
        cart_discount=round(total_cart_discount, 2),
        total_cart_price=round(total_cart_price, 2),
        created_datetime=created_time,
        updated_datetime=updated_time
    )




def merge_carts(request: MergeCartRequest, db: Session) -> CartResponse:
    temp_items = db.query(Cart).filter(Cart.cart_id == request.temp_cart_id).all()
    if not temp_items:
        raise HTTPException(status_code=404, detail="Temporary cart not found")

    filters = []
    if request.customer_id:
        filters.append(Cart.customer_id == request.customer_id)
    if request.guest_user_id:
        filters.append(Cart.guest_user_id == request.guest_user_id)

    existing_cart = db.query(Cart).filter(*filters).all()
    target_cart_id = existing_cart[0].cart_id if existing_cart else str(uuid.uuid4())

    for temp_item in temp_items:
        item = db.query(Item).filter(Item.id == temp_item.item_id).first()
        if not item:
            continue

        item_discount = item.discount or 0.0
        item_price = round(item.item_price * (1 - item_discount / 100), 2)

        match_filters = [
            Cart.cart_id == target_cart_id,
            Cart.item_id == temp_item.item_id
        ]
        if request.customer_id:
            match_filters.append(Cart.customer_id == request.customer_id)
        if request.guest_user_id:
            match_filters.append(Cart.guest_user_id == request.guest_user_id)

        existing_item = db.query(Cart).filter(*match_filters).first()

        if existing_item:
            existing_item.quantity += temp_item.quantity
            existing_item.total_price = round(existing_item.quantity * item_price, 2)
            existing_item.updated_datetime = datetime.utcnow()
        else:
            db.add(Cart(
                cart_id=target_cart_id,
                customer_id=request.customer_id,
                guest_user_id=request.guest_user_id,
                item_id=temp_item.item_id,
                quantity=temp_item.quantity,
                total_price=round(temp_item.quantity * item_price, 2),
                mrp_price=item.item_price,
                created_datetime=datetime.utcnow(),
                updated_datetime=datetime.utcnow()
            ))

    # Delete temporary cart items
    db.query(Cart).filter(Cart.cart_id == request.temp_cart_id).delete()
    db.commit()

    # Prepare final CartResponse
    cart_items_response = []
    total_cart_mrp = 0.0
    total_cart_discount = 0.0
    total_cart_price = 0.0

    all_items = db.query(Cart).filter(Cart.cart_id == target_cart_id).all()

    for entry in all_items:
        item = db.query(Item).filter(Item.id == entry.item_id).first()
        if item:
            item_discount = item.discount or 0.0
            item_price = round(item.item_price * (1 - item_discount / 100), 2)
            cart_items_response.append(CartItemResponse(
                item_id=item.id,
                item_name=item.item_name,
                item_price=item_price,
                mrp_price=item.item_price,
                cart_discount=item_discount,
                quantity=entry.quantity,
                total_price=entry.total_price,
                product_image=item.product_image
            ))

            total_cart_mrp += item.item_price * entry.quantity
            total_cart_discount += (item.item_price * item_discount / 100) * entry.quantity
            total_cart_price += item_price * entry.quantity

    created_time = all_items[0].created_datetime if all_items else datetime.utcnow()
    updated_time = all_items[-1].updated_datetime if all_items else datetime.utcnow()

    return CartResponse(
        cart_id=target_cart_id,
        customer_id=request.customer_id,
        guest_user_id=request.guest_user_id,
        items=cart_items_response,
        mrp_price=round(total_cart_mrp, 2),
        cart_discount=round(total_cart_discount, 2),
        total_cart_price=round(total_cart_price, 2),
        created_datetime=created_time,
        updated_datetime=updated_time
    )



def update_cart_item(request: UpdateCartItemRequest, db: Session) -> CartItemResponse:
    if not request.customer_id and not request.cart_id:
        raise HTTPException(status_code=400, detail="Either customer_id or cart_id is required")

    filters = [Cart.item_id == request.item_id]
    if request.customer_id:
        filters.append(Cart.customer_id == request.customer_id)
    elif request.cart_id:
        filters.append(Cart.cart_id == request.cart_id)

    cart_item = db.query(Cart).filter(*filters).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    item = db.query(Item).filter(Item.id == request.item_id).first()
    cart_item.quantity = request.quantity
    cart_item.total_price = request.quantity * item.item_price

    db.commit()
    db.refresh(cart_item)

    return CartItemResponse(
        item_id=item.id,
        item_name=item.item_name,
        item_price=item.item_price,
        quantity=cart_item.quantity,
        total_price=cart_item.total_price,
        product_image=item.product_image
    )


def remove_cart_item(request: RemoveCartItemRequest, db: Session):
    # Always required
    filters = [Cart.item_id == request.item_id]

    # Add matching condition depending on available identifiers
    if request.customer_id:
        filters.append(Cart.customer_id == request.customer_id)
    elif request.guest_user_id:
        filters.append(Cart.guest_user_id == request.guest_user_id)
    elif request.cart_id:
        filters.append(Cart.cart_id == request.cart_id)
    else:
        raise HTTPException(status_code=400, detail="Must provide customer_id, guest_user_id, or cart_id")

    cart_item = db.query(Cart).filter(*filters).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}




def remove_cart_item(request: RemoveCartItemRequest, db: Session):
    if not request.customer_id and not request.guest_user_id and not request.cart_id:
        raise HTTPException(status_code=400, detail="Provide customer_id, guest_user_id, or cart_id")

    filters = [Cart.item_id == request.item_id]

    if request.customer_id:
        filters.append(Cart.customer_id == request.customer_id)
    elif request.guest_user_id:
        filters.append(Cart.guest_user_id == request.guest_user_id)
    elif request.cart_id:
        filters.append(Cart.cart_id == request.cart_id)

    cart_item = db.query(Cart).filter(*filters).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}




def get_cart_items(
    db: Session,
    customer_id: Optional[str] = None,
    guest_user_id: Optional[str] = None,
    cart_id: Optional[str] = None
) -> CartResponse:
    if not customer_id and not guest_user_id and not cart_id:
        raise HTTPException(status_code=400, detail="Provide customer_id, guest_user_id, or cart_id")

    filters = []
    if customer_id:
        filters.append(Cart.customer_id == customer_id)
    if guest_user_id:
        filters.append(Cart.guest_user_id == guest_user_id)
    if cart_id:
        filters.append(Cart.cart_id == cart_id)

    cart_items = db.query(Cart).filter(*filters).all()

    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty")

    item_responses = []
    total_cart_mrp = 0.0
    total_cart_discount = 0.0
    total_cart_price = 0.0

    for entry in cart_items:
        item = db.query(Item).filter(Item.id == entry.item_id).first()
        if not item:
            continue  # Skip if item is missing

        quantity = entry.quantity
        item_mrp = item.item_price
        base_discount = item.discount or 0.0
        extra_discount = 10.0 if quantity > 5 else 0.0

        # Compounded discount logic
        compounded_factor = (1 - base_discount / 100) * (1 - extra_discount / 100)
        compounded_discount = round((1 - compounded_factor) * 100, 2)

        per_unit_price = round(item_mrp * compounded_factor, 2)
        total_price = round(per_unit_price * quantity, 2)

        total_cart_mrp += item_mrp * quantity
        total_cart_price += total_price
        total_cart_discount += (item_mrp * quantity) - total_price

        item_responses.append(CartItemResponse(
            item_id=item.id,
            item_name=item.item_name,
            item_price=per_unit_price,
            mrp_price=item_mrp,
            cart_discount=compounded_discount,
            quantity=quantity,
            total_price=total_price,
            product_image=item.product_image
        ))

    return CartResponse(
        cart_id=cart_items[0].cart_id,
        customer_id=cart_items[0].customer_id,
        guest_user_id=cart_items[0].guest_user_id,
        items=item_responses,
        mrp_price=round(total_cart_mrp, 2),
        cart_discount=round(total_cart_discount, 2),
        total_cart_price=round(total_cart_price, 2),
        created_datetime=cart_items[0].created_datetime,
        updated_datetime=cart_items[-1].updated_datetime
    )

    
def delete_cart_by_id(cart_id: str, db: Session):
    cart_items = db.query(Cart).filter(Cart.cart_id == cart_id).all()

    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart not found")

    for item in cart_items:
        db.delete(item)

    db.commit()
    return {"message": f"Cart with ID {cart_id} has been deleted"}


def update_cart_item_quantity(cart_id: str, item_id: str, quantity: int, db: Session) -> CartResponse:
    # Find the cart entry
    cart_entry = db.query(Cart).filter(
        Cart.cart_id == cart_id,
        Cart.item_id == item_id
    ).first()

    if not cart_entry:
        raise HTTPException(status_code=404, detail="Cart item not found")

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Recalculate item price
    item_mrp = item.item_price
    item_discount = item.discount
    item_price = round(item_mrp * (1 - item_discount / 100), 2)
    total_price = round(item_price * quantity, 2)

    # Update the cart item
    cart_entry.quantity = quantity
    cart_entry.total_price = total_price
    cart_entry.updated_datetime = datetime.utcnow()
    db.commit()
    db.refresh(cart_entry)

    # Recalculate the whole cart totals
    cart_items = db.query(Cart).filter(Cart.cart_id == cart_id).all()

    cart_items_response = []
    total_cart_mrp = 0.0
    total_cart_discount = 0.0
    total_cart_price = 0.0

    for entry in cart_items:
        item = db.query(Item).filter(Item.id == entry.item_id).first()
        if not item:
            continue

        item_price = round(item.item_price * (1 - item.discount / 100), 2)
        entry_total_price = round(item_price * entry.quantity, 2)

        cart_items_response.append(CartItemResponse(
            item_id=item.id,
            item_name=item.item_name,
            item_price=item_price,
            mrp_price=item.item_price,
            cart_discount=item.discount,
            quantity=entry.quantity,
            total_price=entry_total_price,
            product_image=item.product_image
        ))

        total_cart_mrp += item.item_price * entry.quantity
        total_cart_discount += (item.item_price * item.discount / 100) * entry.quantity
        total_cart_price += entry_total_price

    created_time = cart_items[0].created_datetime if cart_items else datetime.utcnow()
    updated_time = cart_items[-1].updated_datetime if cart_items else datetime.utcnow()

    return CartResponse(
        cart_id=cart_id,
        customer_id=cart_entry.customer_id,
        guest_user_id=cart_entry.guest_user_id,
        items=cart_items_response,
        mrp_price=round(total_cart_mrp, 2),
        cart_discount=round(total_cart_discount, 2),
        total_cart_price=round(total_cart_price, 2),
        created_datetime=created_time,
        updated_datetime=updated_time
    )


