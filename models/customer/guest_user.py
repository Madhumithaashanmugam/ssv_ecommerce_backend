from sqlalchemy import Column, String, TIMESTAMP, text, func
from config.db.session import Base
import uuid

class GuestUser(Base):
    __tablename__ = "guest_user"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)  
    email = Column(String, nullable=True)          

    street_line = Column(String, nullable=False)
    plot_number = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)

    created_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_datetime = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
