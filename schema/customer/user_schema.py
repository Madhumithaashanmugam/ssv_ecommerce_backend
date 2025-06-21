from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# ----------- OTP Flow -----------

class OtpRequest(BaseModel):
    email: EmailStr = Field(..., description="Customer email address for requesting OTP")

class OtpVerify(BaseModel):
    email: EmailStr = Field(..., description="Customer email used for verifying OTP")
    otp: str = Field(..., description="One-Time Password sent to email")

# ----------- Registration -----------

class CreateUserWithOTPCheck(BaseModel):
    name: Optional[str] = Field(None, description="Customer's full name")
    email: EmailStr = Field(..., description="Customer email address")
    phone_number: Optional[str] = Field(None, description="Customer phone number")
    hashed_password: str = Field(..., description="Hashed password for the customer")

class CreateUser(BaseModel):
    name: Optional[str]
    email: EmailStr
    phone_number: Optional[str]
    hashed_password: str
    created_datetime: Optional[datetime] = None
    updated_datetime: Optional[datetime] = None

# ----------- Forgot Password Flow -----------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email to send OTP for password reset")

class ForgotPasswordOTPVerify(BaseModel):
    email: EmailStr = Field(..., description="Email to verify OTP")
    otp: str = Field(..., description="OTP received via email")

class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email for password reset")
    otp: str = Field(..., description="OTP sent to email")
    new_password: str = Field(..., description="New password to set after verification")

# ----------- User Update / View -----------

class UpdateUser(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str]
    created_datetime: datetime
    updated_datetime: datetime

class ViewUser(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone_number: Optional[str]
    created_datetime: Optional[datetime]
    updated_datetime: Optional[datetime]

    class Config:
        orm_mode = True  # ✅ enables parsing SQLAlchemy objects directly


# ----------- Token / Auth -----------

class UserDetails(BaseModel):
    email: EmailStr
    name: str

class TokenData(BaseModel):
    access_token: str
    token_type: str
    user: UserDetails

# ----------- Raw Login Form -----------

class Data(BaseModel):
    name: str
    password: str

    class Config:
        orm_mode = True
