from sqlalchemy import Column, String, Float, Enum as SQLAEnum, TIMESTAMP, text, func, Boolean, JSON
from config.db.session import Base
import uuid
from enum import Enum

class OrderStatus(str, Enum):
    pending = "Pending"
    accepted = "Accepted"
    declined = "Declined"
    completed = "Completed"
    returned = "Returned"

class PaymentMethod(str, Enum):
    online = "Online"
    cod = "Cash On Delivery"

class PaymentStatus(str, Enum):
    pending = "Pending"
    success = "Success"
    failed = "Failed"

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    user_id = Column(String, nullable=True) 
    guest_user_id = Column(String, nullable=True)  
    session_id = Column(String, nullable=True)

    total_price = Column(Float, nullable=False)
    items = Column(JSON, nullable=False)

    order_status = Column(SQLAEnum(OrderStatus), default=OrderStatus.pending, nullable=False)
    payment_method = Column(SQLAEnum(PaymentMethod), nullable=False)
    payment_status = Column(SQLAEnum(PaymentStatus), default=PaymentStatus.pending)
    is_paid = Column(Boolean, default=False)

    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    razorpay_signature = Column(String, nullable=True)

    reason = Column(String, nullable=True)

    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_datetime = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_datetime = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now()
    )
