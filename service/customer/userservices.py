from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from models.customer.user import User
from schema.customer.user_schema import CreateUser, UpdateUser
from passlib.context import CryptContext
import logging
import re
from datetime import datetime
import uuid

import random
from service.sms_service import send_otp_email

logger = logging.getLogger(__name__)

bcrypt_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^\d{10}$')


def validate_email(email: str):
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

def validate_phone(phone: str):
    if not PHONE_REGEX.match(phone):
        raise HTTPException(status_code=400, detail="Phone number must be 10 digits long.")

def validate_password(password: str):
    if not (8 <= len(password) <= 12):
        raise HTTPException(
            status_code=400,
            detail="Password must be between 8 and 12 characters long."
        )


def generate_otp():
    return str(random.randint(100000, 999999))


def request_otp(email: str, session: Session):
    validate_email(email)

    user = session.query(User).filter(User.email == email).first()
    if user and user.is_otp_verified:
        raise HTTPException(status_code=400, detail="Email already registered.")

    otp = generate_otp()

    if not user:
        user = User(email=email, otp=otp, is_otp_verified=False)
        session.add(user)
    else:
        user.otp = otp
        user.is_otp_verified = False

    session.commit()
    send_otp_email(otp, email)
    return {"message": "OTP sent to your email address."}


def verify_otp(email: str, otp: str, session: Session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="email not found.")

    if user.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    user.is_otp_verified = True
    session.commit()
    return {"message": "OTP verified successfully."}


def register_after_otp(user_data: CreateUser, session: Session):
    user = session.query(User).filter(User.email == user_data.email).first()

    if not user or not user.is_otp_verified:
        raise HTTPException(status_code=400, detail="OTP not verified for this phone number.")

    if user.hashed_password:
        raise HTTPException(status_code=400, detail="User already registered.")

    validate_email(user_data.email)
    validate_password(user_data.hashed_password)

    user.name = user_data.name
    user.email = user_data.email
    user.phone_number = user_data.phone_number 
    user.hashed_password = bcrypt_context.hash(user_data.hashed_password)

    session.commit()
    session.refresh(user)
    return user



def delete_user_by_id(id: str, session: Session):
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}


# Forgot Password Functions
def request_reset_password(email: str, session: Session):
    validate_email(email)
    
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")
    
    otp = generate_otp()
    user.otp = otp
    user.is_otp_verified = False  # Require OTP verification again
    session.commit()
    
    # Send OTP to user's email for password reset
    send_otp_email(otp, email)
    return {"message": "OTP sent to your email for password reset."}

def reset_password(email: str, otp: str, new_password: str, session: Session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this phone number not found.")

    if user.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    
    # Password validation
    if not re.search(r'[A-Z]', new_password) or not re.search(r'[a-z]', new_password) or \
       not re.search(r'\d', new_password) or not re.search(r'[\*\@\#\$\!\~\^\(\)\_\-\+\=\<\>\?\;\:\'\",\`\[\]\{\}\.]', new_password) or \
       not (8 <= len(new_password) <= 12):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and must be between 8-12 characters.")
    
    user.hashed_password = bcrypt_context.hash(new_password)
    user.is_otp_verified = True  
    session.commit()
    
    return {"message": "Password reset successfully."}

def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(user_id: str, session: Session):
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


def update_user_by_id(user_id: str, user_data: UpdateUser, session: Session):
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.name = user_data.name
    user.email = user_data.email
    user.phone_number = user_data.phone_number
    user.updated_datetime = datetime.utcnow()

    session.commit()
    session.refresh(user)
    return user