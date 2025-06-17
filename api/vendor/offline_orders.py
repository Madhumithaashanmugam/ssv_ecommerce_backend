from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.db.session import get_db
from models.vendor.offline_orders import OfflineOrder
from schema.vendor.offline_orders import OfflineOrderCreate, OfflineOrderUpdate,OfflineOrderResponse, UpdateOrderReturnStatus
from service.vendor.offline_orders import (
    create_offline_order,
    get_offline_orders,
    get_offline_order_by_id,
    update_offline_order,
    update_order_return_status,
    get_all_returned_orders
)
from utils.jwt_handler import get_current_vendor

offline_router = APIRouter(
)

@offline_router.post("/", response_model=OfflineOrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OfflineOrderCreate,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐
):
    return create_offline_order(db, order)


@offline_router.get("/", response_model=List[OfflineOrderResponse], status_code=status.HTTP_200_OK)
def read_orders(
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐
):
    return get_offline_orders(db)

@offline_router.get("/{order_id}", response_model=OfflineOrderResponse, status_code=status.HTTP_200_OK)
def read_order_by_id(
    order_id: str,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐
):
    return get_offline_order_by_id(db, order_id)

@offline_router.put("/{order_id}", response_model=OfflineOrderResponse, status_code=status.HTTP_200_OK)
def update_order(
    order_id: str,
    order_update: OfflineOrderUpdate,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐
):
    return update_offline_order(db, order_id, order_update)

@offline_router.put("/orders/return-status")
def set_return_status(
    order_data: UpdateOrderReturnStatus,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐
):
    updated_order = update_order_return_status(db, order_data)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order return status updated", "order": updated_order}


@offline_router.get("/orders/returned")
def fetch_returned_orders(
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐
):
    returned_orders = get_all_returned_orders(db)
    return {"returned_orders": returned_orders}
