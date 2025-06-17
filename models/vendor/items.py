from sqlalchemy import Column, String, Float, ForeignKey, func, TIMESTAMP, text, Integer, JSON
from sqlalchemy.orm import relationship
from config.db.session import Base
import uuid

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    item_name = Column(String, nullable=False)
    item_price = Column(Float, nullable=False)
    discount = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    kg = Column(Float, nullable=False)
    quality = Column(String, nullable=False)
    product_image = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=True)
    additional_images = Column(JSON, nullable=True, default=[])# ✅ New field added here

    created_datetime = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_datetime = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", backref="items")
