from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from config.db.session import get_db
from schema.customer.guest_user import GuestUserCreate, GuestUserResponse, GuestUserUpdate
from service.customer.guest_user import create_guest_user, get_guest_user_by_phone, get_all_guest_users, get_guest_user_by_id, update_guest_user
from uuid import UUID

guest_user_router = APIRouter()

@guest_user_router.post("/guest-user/create", response_model=GuestUserResponse)
def create_guest(guest: GuestUserCreate, db: Session = Depends(get_db)):
    return create_guest_user(db, guest)

@guest_user_router.get("/guest-user/{phone_number}", response_model=GuestUserResponse)
def get_guest(phone_number: str, db: Session = Depends(get_db)):
    return get_guest_user_by_phone(db, phone_number)


@guest_user_router.get("/guest-users", response_model=List[GuestUserResponse])
def get_all_guests(db: Session = Depends(get_db)):
    return get_all_guest_users(db)


@guest_user_router.get("/guest-user/id/{guest_user_id}", response_model=GuestUserResponse)
def get_guest_by_id(guest_user_id: UUID, db: Session = Depends(get_db)):
    return get_guest_user_by_id(db, str(guest_user_id))


@guest_user_router.put("/guest-user/update/{guest_user_id}", response_model=GuestUserResponse)
def update_guest(
    guest_user_id: str,
    guest_update: GuestUserUpdate,
    db: Session = Depends(get_db)
):
    return update_guest_user(db, guest_user_id, guest_update)
