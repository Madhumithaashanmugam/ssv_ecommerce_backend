import uuid
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

# -------------------------
# OTP-based Registration Schemas
# -------------------------

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SendOTPRequest(BaseModel):
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class CreateUserRequest(BaseModel):
    name: Optional[str]
    email: str
    phone_number: Optional[str]  # Kept optional in case you still want to store it
    hashed_password: str

class UpdateUser(BaseModel):
    name: str
    email: str
    phone_number: Optional[str]
    created_datetime: datetime
    updated_datetime: datetime

class UserDetails(BaseModel):
    email: str
    name: str

class TokenData(BaseModel):
    access_token: str
    token_type: str
    user: UserDetails

class Data(BaseModel):
    name: str
    password: str

    class Config:
        orm_mode = True

class ForgotPasswordRequest(BaseModel):
    email: str  # Changed from phone_number

class ForgotPasswordOTPVerify(BaseModel):
    email: str  # Changed from phone_number
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str  # Changed from phone_number
    otp: str
    new_password: str

    

class ViewUser(BaseModel):
    id: str    
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    created_datetime: Optional[datetime] = None
    updated_datetime: Optional[datetime] = None

    class Config:
        orm_mode = True

    class Config:
        orm_mode = True