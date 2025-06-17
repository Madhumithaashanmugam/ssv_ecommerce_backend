from models.vendor.items import Item  # Make sure to import the Item model
from sqlalchemy.orm import Session
from models.vendor.offline_orders import OfflineOrder
from schema.vendor.offline_orders import OfflineOrderCreate, OfflineOrderUpdate, UpdateOrderReturnStatus
from fastapi import HTTPException
import uuid


def create_offline_order(db: Session, order: OfflineOrderCreate):
    item_ids = [item.item_id for item in order.items]
    db_items = db.query(Item).filter(Item.id.in_(item_ids)).all()
    db_item_map = {str(item.id): item for item in db_items}

    missing_ids = set(item_ids) - set(db_item_map.keys())
    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid item IDs: {', '.join(missing_ids)}"
        )

    processed_items = []
    gross_total = 0.0  # Total before discount

    for order_item in order.items:
        item = db_item_map[order_item.item_id]
        quantity = order_item.quantity

        if item.quantity < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for item {item.item_name}"
            )

        item_price = item.item_price
        item_discount = item.discount or 0
        final_price = item_price - (item_price * item_discount / 100)
        line_total = final_price * quantity
        gross_total += line_total

        # Decrease inventory
        item.quantity -= quantity

        processed_items.append({
            "item_id": item.id,
            "item_name": item.item_name,
            "item_price": item_price,
            "discount": item_discount,
            "final_price": final_price,
            "quantity": quantity,
            "line_total": line_total
        })

    # Apply overall discount as a percentage on gross_total
    overall_discount_percent = order.discount or 0.0
    discount_amount = gross_total * (overall_discount_percent / 100)
    total_amount = gross_total - discount_amount

    amount_paid = order.amount_paid or 0.0
    balance_due = total_amount - amount_paid

    db_order = OfflineOrder(
        id=str(uuid.uuid4()),
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        order_date=order.order_date,
        delivery_date=order.delivery_date,
        payment_status=order.payment_status,
        payment_method=order.payment_method,
        total_amount=total_amount,
        discount=overall_discount_percent,
        amount_paid=amount_paid,
        balance_due=balance_due,
        created_by=order.created_by,
        notes=order.notes,
        items=processed_items
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order



def get_offline_orders(db: Session):
    return db.query(OfflineOrder).all()



def get_offline_order_by_id(db: Session, order_id: str):
    db_order = db.query(OfflineOrder).filter(OfflineOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Offline order not found")
    return db_order


def update_offline_order(db: Session, order_id: str, order_update: OfflineOrderUpdate):
    db_order = db.query(OfflineOrder).filter(OfflineOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Offline order not found")

    update_data = order_update.dict(exclude_unset=True)

    # If items are being updated, revert previous quantities and apply new ones
    if "items" in update_data:
        # Revert stock quantities from previous order
        previous_items = db_order.items
        for prev in previous_items:
            item = db.query(Item).filter(Item.id == prev["item_id"]).first()
            if item:
                item.quantity += prev["quantity"]

        # Fetch new items
        new_items_raw = update_data["items"]
        item_ids = [item["item_id"] for item in new_items_raw]
        db_items = db.query(Item).filter(Item.id.in_(item_ids)).all()
        db_item_map = {str(item.id): item for item in db_items}

        missing_ids = set(item_ids) - set(db_item_map.keys())
        if missing_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid item IDs: {', '.join(missing_ids)}"
            )

        processed_items = []
        total_amount = 0.0

        for order_item in new_items_raw:
            item = db_item_map[order_item["item_id"]]
            quantity = order_item["quantity"]

            if item.quantity < quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for item {item.item_name}"
                )

            item_price = item.item_price
            discount = item.discount or 0
            final_price = item_price - (item_price * discount / 100)
            line_total = final_price * quantity
            total_amount += line_total

            item.quantity -= quantity  # Reduce stock

            processed_items.append({
                "item_id": item.id,
                "item_name": item.item_name,
                "item_price": item_price,
                "discount": discount,
                "final_price": final_price,
                "quantity": quantity,
                "line_total": line_total
            })

        update_data["items"] = processed_items
        update_data["total_amount"] = total_amount
        update_data["balance_due"] = total_amount - (update_data.get("amount_paid") or db_order.amount_paid or 0)

    for key, value in update_data.items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order

def update_order_return_status(db: Session, order_data: UpdateOrderReturnStatus):
    order = db.query(OfflineOrder).filter(OfflineOrder.id == order_data.order_id).first()
    if not order:
        return None

    # If marking as returned, restock item quantities
    if order_data.is_returned:
        for ordered_item in order.items:
            item_id = ordered_item["item_id"]
            quantity = ordered_item["quantity"]

            item = db.query(Item).filter(Item.id == item_id).first()
            if item:
                item.quantity += quantity
            else:
                raise Exception(f"Item not found for item_id {item_id}")

    order.is_returned = order_data.is_returned
    db.commit()
    db.refresh(order)
    return order


def get_all_returned_orders(db: Session):
    return db.query(OfflineOrder).filter(OfflineOrder.is_returned == True).all()
