from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class GuestUserCreate(BaseModel):
    name: str
    phone_number: str
    email: Optional[EmailStr] = None
    street_line: str
    plot_number: str
    city: str
    state: str
    zip_code: str

class GuestUserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    street_line: Optional[str] = None
    plot_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    
class GuestUserResponse(BaseModel):
    id: str
    name: str
    phone_number: str
    email: Optional[EmailStr] = None
    street_line: str
    plot_number: str
    city: str
    state: str
    zip_code: str
    created_datetime: datetime
    updated_datetime: datetime

    class Config:
        orm_mode = True