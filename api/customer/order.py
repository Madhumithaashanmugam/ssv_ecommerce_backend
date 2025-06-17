from fastapi import APIRouter, Depends, HTTPException,  status
from sqlalchemy.orm import Session
from fastapi import Body
from typing import List
from config.db.session import get_db
from schema.customer.order import CreateOrderRequest, OrderResponse, UpdateOrderStatusRequest, OrderStatus, OrderQueryRequest, OrderReasonUpdate
from service.customer.order import create_order, update_order_status_service, get_all_orders_service, get_orders_by_status_service, get_orders_by_user_or_guest, get_order_by_id, get_orders_by_user_or_guest_service, update_order_reason
from utils.jwt_handler import get_current_vendor

order_router = APIRouter()

@order_router.post("/orders", response_model=OrderResponse)
def place_order(
    request: CreateOrderRequest = Body(...),
    db: Session = Depends(get_db),
) -> OrderResponse:
    try:
        return create_order(request, db)
    except HTTPException:
        # re-raise HTTPExceptions coming from your service
        raise
    except Exception as e:
        # catch & wrap unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

@order_router.put("/orders/{order_id}/status", response_model=dict)
def update_order_status(
    order_id: str,
    request: UpdateOrderStatusRequest,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # ✅ Vendor Authentication Applied
):
    """
    Vendor-protected endpoint to update order status.
    """
    try:
        message = update_order_status_service(order_id, request.order_status, db)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@order_router.get("/orders", response_model=list[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    orders = get_all_orders_service(db)
    return orders

@order_router.get("/orders/status/{status}", response_model=list[OrderResponse])
def get_orders_by_status(status: OrderStatus, db: Session = Depends(get_db)):
    orders = get_orders_by_status_service(status, db)
    if not orders:
        raise HTTPException(status_code=404, detail=f"No orders found with status '{status}'")
    return orders

@order_router.post("/orders/user", response_model=List[OrderResponse])
def get_orders_by_user_or_guest_endpoint(
    request: OrderQueryRequest,
    db: Session = Depends(get_db)
):
    return get_orders_by_user_or_guest(request, db)


@order_router.get("/order/{order_id}", response_model=OrderResponse)
def read_order(order_id: str, db: Session = Depends(get_db)):
    return get_order_by_id(order_id, db)


@order_router.post("/by-user-or-guest", response_model=List[OrderResponse])
def get_orders_by_user_or_guest(
    request: OrderQueryRequest,
    db: Session = Depends(get_db)
):
    return get_orders_by_user_or_guest_service(request, db)


@order_router.put("/orders/reason", status_code=status.HTTP_200_OK)
def fill_order_reason(
    order_data: OrderReasonUpdate,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # ✅ Vendor Authentication Applied
):
    updated_order = update_order_reason(order_data, db)
    return {
        "success": True,
        "message": "Order reason updated successfully",
        "data": {
            "order_id": updated_order.id,
            "reason": updated_order.reason
        }
    }