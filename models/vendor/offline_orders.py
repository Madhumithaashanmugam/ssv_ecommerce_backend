from sqlalchemy import Column, String, Float, Date, Enum as SQLAEnum, Text, TIMESTAMP, text, func, Boolean
from sqlalchemy.dialects.postgresql import JSON
from config.db.session import Base
import uuid

class OfflineOrder(Base):
    __tablename__ = "offline_orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_address = Column(Text, nullable=True)

    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=True)

    payment_status = Column(
        SQLAEnum("Paid", "Unpaid", "Partial", name="payment_status_enum"),
        nullable=False
    )
    payment_method = Column(
        SQLAEnum("Cash", "Bank Transfer", "UPI", name="payment_method_enum"),
        nullable=False
    )

    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)

    created_by = Column(String, nullable=False)
    notes = Column(Text, nullable=True)

    items = Column(JSON, nullable=False, default=[])
    is_returned = Column(Boolean, default=False) 

    created_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


