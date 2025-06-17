from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config.db.session import get_db
from models.customer.user import User
from passlib.context import CryptContext
from utils.jwt_handler import create_access_token

auth_router = APIRouter(prefix="/customer/auth", tags=["Customer Auth"])

# Use the same hashing schemes as during registration
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


@auth_router.post("/login")
def customer_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Look up the user by email (used as username in OAuth2 form)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create the access token
    token = create_access_token(
        data={
            "sub": user.email,
            "id": str(user.id),
            "name": user.name
        },
        user_type="customer"
    )

    # ✅ Return both token and user info
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number
        }
    }
