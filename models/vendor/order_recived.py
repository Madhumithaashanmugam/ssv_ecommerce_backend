from sqlalchemy import Column, String, Float, TIMESTAMP, text, func, ForeignKey
from sqlalchemy.orm import relationship
from config.db.session import Base
import uuid
class OrderReceived(Base):
    __tablename__ = "order_received"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    customer_id = Column(String, ForeignKey("customer_user.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendor_user.id"), nullable=False)

    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    total_amount = Column(Float, nullable=False)

    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)

    ordered_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    delivered_date = Column(TIMESTAMP(timezone=True), nullable=True)

    payment_status = Column(String, nullable=False)
    order_status = Column(String, nullable=False, default="Pending")

    customer = relationship("models.customer.user.User")

    updated_datetime = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
