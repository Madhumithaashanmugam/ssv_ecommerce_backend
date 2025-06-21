from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Utils
from utils.jwt_handler import create_access_token
import logging

logger = logging.getLogger(__name__)



# Database
from config.db.session import get_db

# Models
from models.customer.user import User

# Schemas
from schema.customer.user_schema import (
    CreateUser,
    UpdateUser,
    ViewUser,
    OtpRequest,
    OtpVerify,
    CreateUserWithOTPCheck,
    ResetPasswordRequest,
    ForgotPasswordOTPVerify,
    ForgotPasswordRequest
    
)

# Services
from service.customer.userservices import (
    # update_user_by_id,
    delete_user_by_id,
    request_otp,
    verify_otp,
    register_after_otp,
    request_reset_password,
    reset_password,
    get_user_by_id,
    update_user_by_id
)

# Routers
user_router = APIRouter(prefix="/customer/users", tags=["Customer Users"])
auth_router = APIRouter(prefix="/auth")

# ----------------------------------------
#           OTP BASED REGISTRATION
# ----------------------------------------

@auth_router.post("/request-otp")
def send_otp(payload: OtpRequest, db: Session = Depends(get_db)):
    return request_otp(payload.email, db)


@auth_router.post("/verify-otp")
def check_otp(payload: OtpVerify, db: Session = Depends(get_db)):
    return verify_otp(payload.email, payload.otp, db)


@auth_router.post("/register")
def complete_registration(user: CreateUserWithOTPCheck, db: Session = Depends(get_db)):
    created_user = register_after_otp(user, db)
    token = create_access_token(
        data={"sub": created_user.email, "role": "customer"},
        user_type="customer"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": created_user.id,
            "name": created_user.name,
            "email": created_user.email,
            "phone_number": created_user.phone_number
        }
    }
    

# ----------------------------------------
#           CUSTOMER USER ROUTES
# ----------------------------------------

@user_router.get("/", response_model=list[ViewUser], status_code=status.HTTP_200_OK)
def list_customer_users(db: Session = Depends(get_db)):
    return db.query(User).filter(User.hashed_password.isnot(None)).all()



    
# @user_router.get("/user_id}", response_model=ViewUser)
# def read_user_by_id(user_id: str, db: Session = Depends(get_db)):
#     return get_user_by_id(user_id, db)


# @user_router.put("/{user_id}", response_model=ViewUser, status_code=status.HTTP_200_OK)
# def update_customer_user(user_id: str, user: UpdateUser, db: Session = Depends(get_db)):
#     updated_user = update_user_by_id(user_id, user, db)
#     if not updated_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return updated_user


@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_customer_user(user_id: str, db: Session = Depends(get_db)):
    return delete_user_by_id(user_id, db)


# ----------------------------------------
#           FORGOT PASSWORD API ROUTES
# ----------------------------------------

@user_router.get("/user/{user_id}", response_model=ViewUser)
def read_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(user_id, db)
    return user

@auth_router.post("/request-reset-otp")
def request_reset_otp(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request OTP to reset the password for the provided phone number.
    Sends an OTP to the user's phone number.
    """
    return request_reset_password(payload.email, db)

@auth_router.post("/verify-reset-otp")
def verify_reset_otp(payload: ForgotPasswordOTPVerify, db: Session = Depends(get_db)):
    """
    Verify the OTP sent for resetting the password.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.otp != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    
    user.is_otp_verified = True
    db.commit()
    return {"message": "OTP verified successfully."}

@auth_router.post("/reset-password")
def reset_user_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset the user's password after OTP verification.
    """
    return reset_password(payload.email, payload.otp, payload.new_password, db)


@user_router.put("/user/{user_id}", response_model=ViewUser)
def update_user(user_id: str, user_data: UpdateUser, db: Session = Depends(get_db)):
    return update_user_by_id(user_id, user_data, db)