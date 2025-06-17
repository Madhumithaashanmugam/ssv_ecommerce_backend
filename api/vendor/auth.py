from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config.db.session import get_db
from models.vendor.user import User
from passlib.context import CryptContext
from utils.jwt_handler import create_access_token, SECRET_KEY_VENDOR, ALGORITHM
from service.sms_service import send_email
from jose import jwt, JWTError
import random

auth_router = APIRouter(prefix="/vendor/auth", tags=["Vendor Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction from header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/vendor/auth/login-step1")

# ✅ OTP generator
def generate_otp():
    return str(random.randint(100000, 999999))

# ✅ Step 1: Verify email/password and send OTP
@auth_router.post("/login-step1")
def login_step1(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    otp = generate_otp()
    user.otp = otp
    db.commit()

    # Email message to the OWNER with the user's phone/email and OTP
    subject = "🚨 Login Attempt Alert"
    body = (
        f"The user with phone number {user.phone_number} is trying to log in to your secured vendor account.\n\n"
        f"If you want to allow this login, share the OTP with them: {otp}\n\n"
        f"If this was not expected, you can safely ignore this message."
    )

    
    owner_email = "madhumithaashanmugam@gmail.com"  # replace with actual owner email

    send_email(subject, body, owner_email)

    return {"message": "OTP sent to the owner for verification via email."}
# ✅ Step 2: Verify OTP and return token
@auth_router.post("/login-step2")
def login_step2(
    email: str,
    otp: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or user.otp != otp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")

    # Clear OTP after successful login
    user.otp = None
    db.commit()

    # Create an access token for the logged-in user
    token = create_access_token(
        data={
            "sub": user.email,
            "id": str(user.id),
            "name": user.name,
            "token_version": user.token_version  # ✅ add this line
        },
        user_type="vendor"
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "active_orders": user.active_orders or [],
            "decline_orders": user.decline_orders or [],
            "completed_orders": user.completed_orders or [],
            "created_datetime": str(user.created_datetime),
            "updated_datetime": str(user.updated_datetime)
        }
    }

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY_VENDOR, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        token_version = payload.get("token_version")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.token_version != token_version:
        raise HTTPException(status_code=401, detail="Token expired or invalidated")

    return user

