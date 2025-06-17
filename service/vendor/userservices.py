import random
import re
from service.sms_service import send_otp_email
import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from datetime import datetime
from models.vendor.user import User
from schema.vendor.user_schema import CreateUserRequest,UpdateUser



# Initialize logger
logger = logging.getLogger(__name__)

# Password hashing context
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Regex patterns
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^\d{10}$')

# ----------------------- Validators -----------------------

def validate_email(email: str):
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

def validate_phone(phone: str):
    if not PHONE_REGEX.match(phone):
        raise HTTPException(status_code=400, detail="Phone number must be 10 digits long.")

def validate_password(password: str):
    errors = []
    if not re.search(r'[A-Z]', password):
        errors.append("at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("at least one lowercase letter")
    if not re.search(r'\d', password):
        errors.append("at least one number")

    if not (8 <= len(password) <= 12):
        errors.append("between 8 and 12 characters long")

    if errors:
        raise HTTPException(
            status_code=400,
            detail="Password must contain " + ", ".join(errors) + "."
        )

# ----------------------- OTP Generation -----------------------

def generate_otp():
    return str(random.randint(100000, 999999))

# ----------------------- OTP Request -----------------------
def request_vendor_otp(email: str, session: Session):
    validate_email(email)

    vendor = session.query(User).filter(User.email == email).first()

    if vendor:
        # Email already exists — raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # Email not present — create new user
    otp = generate_otp()
    new_vendor = User(
        id=str(uuid.uuid4()),
        email=email,
        otp=otp,
        is_otp_verified=False,
    )
    session.add(new_vendor)
    session.commit()
    send_otp_email(otp, email)

    return {"message": "OTP sent to your email address."}


# ----------------------- OTP Verification -----------------------

def verify_vendor_otp(email: str, otp: str, session: Session):
    vendor = session.query(User).filter(User.email == email).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Email not found.")

    if vendor.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    vendor.is_otp_verified = True
    session.commit()
    logger.info(f"✅ OTP verified for {email}")
    return {"message": "OTP verified successfully."}


# ----------------------- Registration After OTP -----------------------

def register_vendor_after_otp(vendor_data: CreateUserRequest, session: Session):
    try:
        vendor = session.query(User).filter(User.email == vendor_data.email).first()

        if not vendor or not vendor.is_otp_verified:
            raise HTTPException(status_code=400, detail="OTP not verified for this email.")

        if vendor.hashed_password:
            raise HTTPException(status_code=400, detail="Vendor already registered.")

        validate_email(vendor_data.email)
        validate_password(vendor_data.hashed_password)

        vendor.name = vendor_data.name
        vendor.phone_number = vendor_data.phone_number
        vendor.hashed_password = bcrypt_context.hash(vendor_data.hashed_password)

        session.commit()
        session.refresh(vendor)
        logger.info(f"✅ Vendor registered: {vendor.email}")
        return vendor

    except IntegrityError:
        session.rollback()
        logger.error("❌ Vendor with this email or phone already exists.")
        raise HTTPException(status_code=400, detail="Vendor with this email or phone already exists.")
    except HTTPException as e:
        logger.error(f"❌ Error during registration: {e.detail}")
        raise e
    except Exception as e:
        session.rollback()
        logger.exception("❌ Unexpected error during vendor registration.")
        raise HTTPException(status_code=500, detail="Internal server error")



def update_user_by_id(id: str, user_data: UpdateUser, session: Session):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    user.updated_datetime = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info(f"🔄 User updated: {user.id}")
    return user

def delete_user_by_id(id: str, session: Session):
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    logger.info(f"🗑️ User deleted: {id}")
    return {"message": "User deleted successfully"}

def request_reset_password(email: str, session: Session):
    validate_email(email)
    user = session.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")
    
    otp = generate_otp()
    user.otp = otp
    user.is_otp_verified = False  # Require re-verification
    session.commit()
    
    # Send OTP to user's email for password reset
    send_otp_email(otp, email)
    return {"message": "OTP sent to your email for password reset."}

def reset_password(email: str, otp: str, new_password: str, session: Session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")

    if user.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    
    # Password validation
    if not re.search(r'[A-Z]', new_password) or not re.search(r'[a-z]', new_password) or \
       not (8 <= len(new_password) <= 12):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and must be between 8-12 characters."
        )
    
    user.hashed_password = bcrypt_context.hash(new_password)
    user.is_otp_verified = True  
    session.commit()
    
    return {"message": "Password reset successfully."}




def get_vendor_by_id(id: str, session: Session):
    vendor = session.query(User).filter(User.id == id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    logger.info(f"📦 Vendor retrieved: {vendor.id}")
    return vendor

