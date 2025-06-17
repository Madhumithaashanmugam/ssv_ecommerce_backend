from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schema.vendor.user_schema import CreateUserRequest, UpdateUser, ViewUser, ForgotPasswordOTPVerify, ForgotPasswordRequest, ResetPasswordRequest, ViewUser
from service.vendor.userservices import request_vendor_otp,verify_vendor_otp, update_user_by_id, delete_user_by_id,register_vendor_after_otp, request_reset_password, reset_password, get_vendor_by_id
from config.db.session import get_db
from models.vendor.user import User
from utils.jwt_handler import create_access_token  # ✅ import your token generator
from typing import List 
from utils.jwt_handler import get_current_vendor

user_router = APIRouter(
    tags=["Vendor Users"]
)


user_router = APIRouter(tags=["Vendor Users"])

@user_router.post("/request-otp", status_code=status.HTTP_200_OK)
def request_otp(email: str, db: Session = Depends(get_db)):
    return request_vendor_otp(email, db)

@user_router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    return verify_vendor_otp(email, otp, db)

@user_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_vendor(user_data: CreateUserRequest, db: Session = Depends(get_db)):
    try:
        created_vendor = register_vendor_after_otp(user_data, db)

        # 🔐 Generate JWT token
        token = create_access_token(
            data={"sub": created_vendor.email, "role": "vendor"},
            user_type="vendor"
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": created_vendor.id,
                "name": created_vendor.name,
                "email": created_vendor.email,
                "phone_number": created_vendor.phone_number
            }
        }

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@user_router.put("/{user_id}", response_model=ViewUser, status_code=status.HTTP_200_OK)
def update_vendor_user(
    user_id: str,
    user: UpdateUser,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor auth
):
    updated_user = update_user_by_id(user_id, user, db)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_vendor_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor auth
):
    try:
        return delete_user_by_id(user_id, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@user_router.get("/{user_id}", response_model=ViewUser, status_code=status.HTTP_200_OK)
def get_vendor_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor auth
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@user_router.get("/get-all-login-users", response_model=list[ViewUser], status_code=status.HTTP_200_OK)
def list_vendor_users(
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor auth
):
    users = db.query(User).all()
    return users

@user_router.post("/request-reset-otp", status_code=status.HTTP_200_OK)
def request_reset_otp(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return request_reset_password(payload.email, db)  # ✅ correct


@user_router.post("/verify-reset-otp")
def verify_reset_otp(payload: ForgotPasswordOTPVerify, db: Session = Depends(get_db)):
    """
    Verify the OTP sent for resetting the password.
    """
    user = db.query(User).filter(User.email == payload.email).first()  # ✅ Corrected
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.otp != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    
    user.is_otp_verified = True
    db.commit()
    return {"message": "OTP verified successfully."}


@user_router.post("/reset-password")
def reset_user_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset the user's password after OTP verification.
    """
    return reset_password(payload.email, payload.otp, payload.new_password, db)
@user_router.get("/{vendor_id}", response_model=ViewUser)
def read_vendor_by_id(
    vendor_id: str,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor auth
):
    return get_vendor_by_id(vendor_id, db)