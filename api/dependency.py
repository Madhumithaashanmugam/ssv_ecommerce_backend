from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_handler import decode_access_token

oauth2_scheme_vendor = OAuth2PasswordBearer(tokenUrl="/vendor/auth/login-step2")
oauth2_scheme_customer = OAuth2PasswordBearer(tokenUrl="/customer/auth/login")

def get_current_vendor(token: str = Depends(oauth2_scheme_vendor)):
    payload = decode_access_token(token, user_type="vendor")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid vendor token")
    return payload

def get_current_customer(token: str = Depends(oauth2_scheme_customer)):
    payload = decode_access_token(token, user_type="customer")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid customer token")
    return payload
