from sqlalchemy import Boolean, Column, String, func, Enum as SQLAEnum, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import ARRAY
from config.db.session import Base
import uuid

class User(Base):
    __tablename__ = "customer_user"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    phone_number = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)

    otp = Column(String, nullable=True)  # ✅ NEW FIELD
    is_otp_verified = Column(Boolean, default=False)  # ✅ NEW FIELD

    active_orders = Column(ARRAY(String), default=list)
    decline_orders = Column(ARRAY(String), default=list)
    completed_orders = Column(ARRAY(String), default=list)

    created_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
