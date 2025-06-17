from sqlalchemy import Column, String, Integer, Float, ForeignKey, TIMESTAMP, text, func
from sqlalchemy.orm import relationship
from config.db.session import Base
import uuid
from models.customer.user import User as CustomerUser
from models.vendor.items import Item
from models.customer.guest_user import GuestUser  

class Cart(Base):
    __tablename__ = "carts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Used to identify carts before user is registered/logged in
    cart_id = Column(String, index=True, default=lambda: str(uuid.uuid4()))

    customer_id = Column(String, ForeignKey("customer_user.id"), nullable=True)
    guest_user_id = Column(String, ForeignKey("guest_user.id"), nullable=True)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)  # Final price after discount

    mrp_price = Column(Float, nullable=False, default=0.0)   # item_price × quantity
    discount = Column(Float, nullable=False, default=0.0)    # % discount
    final_price = Column(Float, nullable=False, default=0.0) # final_price = item_price × (1 - discount%) × quantity

    created_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    customer = relationship(CustomerUser, backref="cart_items")
    guest_user = relationship(GuestUser, backref="cart_items")
    item = relationship(Item)
