from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Constants
SECRET_KEY_VENDOR = "nMjpChKFyLlCU8WYzDucqzE1-Oswka8cfw3tTiSgn6U"
SECRET_KEY_CUSTOMER = "agaNRM7XUG_ejrqk1mP352gEOZR0mkAJrCSFP_5FxD8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 525600  # ✅ 1 year

# Bearer scheme for Swagger UI
bearer_scheme = HTTPBearer(auto_error=True)

# ✅ Create access token
def create_access_token(data: dict, user_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "user_type": user_type,
        "token_version": data.get("token_version")
    })
    secret = SECRET_KEY_VENDOR if user_type == "vendor" else SECRET_KEY_CUSTOMER
    encoded_token = jwt.encode(to_encode, secret, algorithm=ALGORITHM)

    print("🕒 Token Expires At:", expire.isoformat())
    return encoded_token

# ✅ Decode access token
def decode_access_token(token: str, user_type: str) -> Optional[dict]:
    secret = SECRET_KEY_VENDOR if user_type == "vendor" else SECRET_KEY_CUSTOMER
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ✅ Auth dependency: Vendor
def get_current_vendor(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY_VENDOR, algorithms=[ALGORITHM])
        if payload.get("user_type") != "vendor":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a vendor token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired vendor token")

# ✅ Auth dependency: Customer
def get_current_customer(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY_CUSTOMER, algorithms=[ALGORITHM])
        if payload.get("user_type") != "customer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a customer token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired customer token")
