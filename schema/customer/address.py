from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AddressCreate(BaseModel):
    customer_id: str
    address_line: str
    city: str
    state: str
    zip_code: str
    extra_details: Optional[str] = None


class AddressUpdate(BaseModel):
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    extra_details: Optional[str] = None


class AddressResponse(BaseModel):
    id: str
    customer_id: str
    address_line: str
    city: str
    state: str
    zip_code: str
    extra_details: Optional[str]
    created_datetime: datetime
    updated_datetime: datetime

    class Config:
        orm_mode = True
