from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List
from schema.vendor.item_schema import ItemOut

class CategoryBase(BaseModel):
    category_name: str

class CategoryCreate(CategoryBase):
    vendor_id: str

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None

class CategoryOut(CategoryBase):
    id: str
    vendor_id: str
    created_datetime: datetime
    updated_datetime: datetime
    
class CategoryWithItemsOut(CategoryOut):
    items: List[ItemOut] = []

    class Config:
        orm_mode = True
