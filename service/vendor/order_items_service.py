from sqlalchemy.orm import Session
from models.customer.order import Order
from models.vendor.order_items import OrderItem
from schema.vendor.order_items_schema import OrderResponseSchema


def get_all_orders_with_items(db: Session):
    orders = db.query(Order).all()
    return [OrderResponseSchema.from_orm(order) for order in orders]

def get_orders_by_customer_id(db: Session, customer_id: str):
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return [OrderResponseSchema.from_orm(order) for order in orders]
