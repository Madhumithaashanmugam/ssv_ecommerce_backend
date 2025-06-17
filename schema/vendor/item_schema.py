from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from datetime import datetime

class ItemBase(BaseModel):
    item_name: str
    item_price: Optional[float] = None
    discount: Optional[float] = None
    final_price: Optional[float] = None
    kg: Optional[float] = None
    quality: str
    product_image: Optional[str] = None
    quantity: int
    description: Optional[str] = None
    additional_images: Optional[List[str]] = []  # ✅ New field added

    @model_validator(mode="before")
    @classmethod
    def parse_numeric_strings(cls, data):
        for field in ['item_price', 'final_price', 'discount', 'kg']:
            value = data.get(field)
            if isinstance(value, str):
                if value.strip() == "":
                    data[field] = None
                else:
                    try:
                        data[field] = float(value.replace(',', '').replace('%', ''))
                    except ValueError:
                        raise ValueError(f"{field} must be a valid number")
        return data

    @field_validator('item_name', mode='before')
    @classmethod
    def strip_item_name(cls, value: str):
        return value.strip()


class ItemCreate(ItemBase):
    category_id: str


class ItemUpdate(BaseModel):
    item_name: Optional[str] = None
    item_price: Optional[float] = None
    discount: Optional[float] = None
    final_price: Optional[float] = None
    kg: Optional[float] = None
    quality: Optional[str] = None
    product_image: Optional[str] = None
    quantity: Optional[int] = None
    description: Optional[str] = None
    additional_images: Optional[List[str]] = None 

    @model_validator(mode="before")
    @classmethod
    def parse_numeric_strings(cls, data):
        for field in ['item_price', 'final_price', 'discount', 'kg']:
            value = data.get(field)
            if isinstance(value, str):
                if value.strip() == "":
                    data[field] = None
                else:
                    try:
                        data[field] = float(value.replace(',', '').replace('%', ''))
                    except ValueError:
                        raise ValueError(f"{field} must be a valid number")
        return data

    @field_validator('item_name', mode='before')
    @classmethod
    def strip_optional_item_name(cls, value: Optional[str]):
        return value.strip() if value else value


class ItemOut(BaseModel):
    id: str
    category_id: str
    item_name: str
    item_price: float
    discount: Optional[float]
    final_price: Optional[float] = None
    kg: float
    quality: str
    product_image: Optional[str]
    quantity: int
    description: Optional[str]
    additional_images: Optional[List[str]] = None  # ✅ New field added
    created_datetime: datetime
    updated_datetime: datetime

    class Config:
        orm_mode = True
