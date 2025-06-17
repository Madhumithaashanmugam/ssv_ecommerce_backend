from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.customer.order import Order, OrderStatus, PaymentStatus
from models.customer.cart import Cart
from models.customer.user import User as CustomerUser
from models.vendor.user import User as VendorUser
from models.vendor.items import Item
from schema.customer.order import CreateOrderRequest, OrderResponse,OrderStatus, OrderQueryRequest, OrderReasonUpdate, OrderItem
from sqlalchemy import func
from datetime import datetime
from models.customer.user import User
from models.customer.guest_user import GuestUser
from typing import List
from service.sms_service import send_order_decline_email
import uuid
import json

def create_order(request: CreateOrderRequest, db: Session) -> OrderResponse:
    if not request.user_id and not request.guest_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or guest_user_id must be provided.")

    total_price = 0.0
    order_items = []

    for item_input in request.items:
        item = db.query(Item).filter(Item.id == item_input.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with ID {item_input.item_id} not found.")
        if item.quantity < item_input.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for item '{item.item_name}'. Only {item.quantity} left."
            )

        item.quantity -= item_input.quantity
        db.add(item)

        # ✅ Apply only base discount on MRP price
        mrp_price = item_input.mrp_price
        base_discount = item_input.discount
        discounted_unit_price = mrp_price * (1 - base_discount / 100)

        quantity = item_input.quantity
        total_for_item = discounted_unit_price * quantity
        total_price += total_for_item

        order_items.append({
            "item_id": item_input.item_id,
            "item_name": item_input.item_name,
            "mrp_price": mrp_price,
            "unit_price": discounted_unit_price,
            "discount": base_discount,
            "additional_discount": item_input.additional_discount,  # only for info
            "quantity": quantity,
            "total_price": total_for_item,
            "product_image": item_input.product_image,
            "note": item_input.note
        })

    order = Order(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        guest_user_id=request.guest_user_id,
        total_price=total_price,
        items=order_items,
        payment_method=request.payment_method,
        payment_status=PaymentStatus.pending,
        is_paid=False,
        address=request.address,
        city=request.city,
        state=request.state,
        created_datetime=datetime.utcnow(),
        updated_datetime=datetime.utcnow()
    )

    db.add(order)

    # 🧹 Clear cart
    if request.user_id:
        db.query(Cart).filter(Cart.customer_id == request.user_id).delete()
    elif request.guest_user_id:
        db.query(Cart).filter(Cart.guest_user_id == request.guest_user_id).delete()

    db.commit()
    db.refresh(order)

    return OrderResponse.from_orm(order)


def update_order_status_service(order_id: str, status: OrderStatus, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise Exception("Order not found")

    # If marking as 'Returned', restock item quantities
    if status == OrderStatus.returned:
        for ordered_item in order.items:
            item_id = ordered_item["item_id"]
            quantity = ordered_item["quantity"]

            item = db.query(Item).filter(Item.id == item_id).first()
            if item:
                item.quantity += quantity
            else:
                raise Exception(f"Item not found for item_id {item_id}")

    # Update the order status
    order.order_status = status.value

    # Set payment status and is_paid based on order status
    if status == OrderStatus.completed:
        order.is_paid = True
        order.payment_status = PaymentStatus.success
    else:
        order.is_paid = False
        order.payment_status = PaymentStatus.pending

    db.commit()
    return "Order status updated"



def get_all_orders_service(db: Session) -> List[Order]:
    return db.query(Order).all()





def get_orders_by_status_service(status: OrderStatus, db: Session) -> List[OrderResponse]:
    orders = db.query(Order).filter(Order.order_status == status).all()
    order_responses = []

    for order in orders:
        # Parse items if stored as JSON string
        items_data = order.items
        if isinstance(items_data, str):
            try:
                items_data = json.loads(items_data)
            except json.JSONDecodeError:
                items_data = []
                print(f"⚠️ Failed to decode items JSON for order ID: {order.id}")

        items = []
        for item in items_data:
            items.append(OrderItem(
                item_id=item.get("item_id"),
                item_name=item.get("item_name"),
                quantity=item.get("quantity", 0),
                unit_price=item.get("unit_price", item.get("item_price", 0.0)),
                total_price=item.get("total_price", 0.0),  # Prevent KeyError here
                discount=item.get("discount", 0.0),
                additional_discount=item.get("additional_discount", 0.0),
                product_image=item.get("product_image"),
                note=item.get("note", "")
            ))

        order_responses.append(OrderResponse(
            id=order.id,
            user_id=order.user_id,
            guest_user_id=order.guest_user_id,
            total_price=order.total_price,
            items=items,
            order_status=order.order_status,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            is_paid=order.is_paid,
            reason=order.reason,
            razorpay_order_id=order.razorpay_order_id,
            razorpay_payment_id=order.razorpay_payment_id,
            razorpay_signature=order.razorpay_signature,
            address=order.address,
            city=order.city,
            state=order.state,
            created_datetime=order.created_datetime,
            updated_datetime=order.updated_datetime
        ))

    return order_responses



def get_orders_by_user_or_guest(request: OrderQueryRequest, db: Session) -> List[OrderResponse]:
    if not request.user_id and not request.guest_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or guest_user_id must be provided.")

    query = db.query(Order)
    if request.user_id:
        query = query.filter(Order.user_id == request.user_id)
    elif request.guest_user_id:
        query = query.filter(Order.guest_user_id == request.guest_user_id)

    orders = query.order_by(Order.created_datetime.desc()).all()
    return [OrderResponse.from_orm(order) for order in orders]

def get_order_by_id(order_id: str, db: Session) -> OrderResponse:
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Explicitly assign all fields including Razorpay ones, even if unused
    return OrderResponse(
    id=order.id,
    user_id=order.user_id,
    guest_user_id=order.guest_user_id,
    total_price=order.total_price,
    items=order.items,
    payment_method=order.payment_method,
    payment_status=order.payment_status,
    is_paid=order.is_paid,
    address=order.address,
    city=order.city,
    state=order.state,
    created_datetime=order.created_datetime,
    updated_datetime=order.updated_datetime,
    razorpay_order_id=order.razorpay_order_id,
    razorpay_payment_id=order.razorpay_payment_id,
    razorpay_signature=order.razorpay_signature,
    order_status=order.order_status,

)


def get_orders_by_user_or_guest_service(request: OrderQueryRequest, db: Session) -> List[OrderResponse]:
    if not request.user_id and not request.guest_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or guest_user_id must be provided.")

    query = db.query(Order)
    
    if request.user_id:
        query = query.filter(Order.user_id == request.user_id)
    elif request.guest_user_id:
        query = query.filter(Order.guest_user_id == request.guest_user_id)

    orders = query.order_by(Order.created_datetime.desc()).all()
    return [OrderResponse.from_orm(order) for order in orders]


def update_order_reason(order_data: OrderReasonUpdate, db: Session):
    order = db.query(Order).filter(Order.id == order_data.order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 🟡 Update reason
    order.reason = order_data.reason
    db.commit()
    db.refresh(order)

    # 🟢 Get email from user or guest_user
    email = None

    if order.user_id:
        user = db.query(User).filter(User.id == order.user_id).first()
        email = user.email if user else None

    elif order.guest_user_id:
        guest = db.query(GuestUser).filter(GuestUser.id == order.guest_user_id).first()
        email = guest.email if guest else None

    # 🔵 Send Email with decline reason
    if email:
        send_order_decline_email(order.reason, email)
    else:
        print(f"[INFO] No email found for order {order.id}. Skipping email.")

    return order
