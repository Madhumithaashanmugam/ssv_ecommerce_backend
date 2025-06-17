# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from config.db.session import get_db
# from service.vendor.order_items_service import get_all_orders_with_items, get_orders_by_customer_id
# from schema.vendor.order_items_schema import OrderResponseSchema
# from typing import List

# order_items_router = APIRouter(
# )

# @order_items_router.get("/", response_model=List[OrderResponseSchema])
# def get_all_orders(db: Session = Depends(get_db)):
#     return get_all_orders_with_items(db)


# @order_items_router.get("/customer/{customer_id}", response_model=List[OrderResponseSchema])
# def get_orders_for_customer(customer_id: str, db: Session = Depends(get_db)):
#     orders = get_orders_by_customer_id(db, customer_id)
#     if not orders:
#         raise HTTPException(status_code=404, detail="No orders found for this customer.")
#     return orders
