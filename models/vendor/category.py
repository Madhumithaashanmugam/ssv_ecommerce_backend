from sqlalchemy import Column, String, ForeignKey, func, TIMESTAMP, text
from sqlalchemy.orm import relationship
from config.db.session import Base
import uuid

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    vendor_id = Column(String, ForeignKey("vendor_user.id"), nullable=False)
    category_name = Column(String, nullable=False)
    created_datetime = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_datetime = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    vendor = relationship("models.vendor.user.User", backref="categories")

