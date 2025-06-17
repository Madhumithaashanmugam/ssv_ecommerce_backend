from sqlalchemy import Column, String, func, TIMESTAMP, text, Integer, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from config.db.session import Base
import uuid

class User(Base):
    __tablename__ = "vendor_user"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)

    name = Column(String)
    phone_number = Column(String, unique=True)
    otp = Column(String, nullable=True)
    is_otp_verified = Column(Boolean, default=False)
    token_version = Column(Integer, default=0)

    active_orders = Column(
        ARRAY(String),
        nullable=False,
        server_default=text("ARRAY[]::VARCHAR[]")  # Ensuring it defaults to an empty array
    )
    decline_orders = Column(
        ARRAY(String),
        nullable=False,
        server_default=text("ARRAY[]::VARCHAR[]")  # Ensuring it defaults to an empty array
    )
    completed_orders = Column(
        ARRAY(String),
        nullable=False,
        server_default=text("ARRAY[]::VARCHAR[]")  # Ensuring it defaults to an empty array
    )

    created_datetime = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_datetime = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )
