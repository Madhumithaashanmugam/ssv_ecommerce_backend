from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, text, func
from sqlalchemy.orm import relationship
from config.db.session import Base
import uuid
from models.customer.user import User as CustomerUser

class Address(Base):
    __tablename__ = "addresses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    customer_id = Column(String, ForeignKey("customer_user.id"), nullable=False)
    address_line = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    extra_details = Column(String, nullable=True)

    created_datetime = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_datetime = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    customer = relationship(CustomerUser)
