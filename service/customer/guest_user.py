import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from models.customer.guest_user import GuestUser
from schema.customer.guest_user import GuestUserCreate, GuestUserResponse, GuestUserUpdate
from typing import Optional

# === Validations ===
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^\d{10}$')

def validate_email(email: str):
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

def validate_phone(phone: str):
    if not PHONE_REGEX.match(phone):
        raise HTTPException(status_code=400, detail="Phone number must be 10 digits long.")

# === Create Guest User ===
def create_guest_user(db: Session, guest_data: GuestUserCreate) -> GuestUser:
    # Validate phone and email
    validate_phone(guest_data.phone_number)
    if guest_data.email:
        validate_email(guest_data.email)

    new_guest = GuestUser(
        name=guest_data.name,
        phone_number=guest_data.phone_number,
        email=guest_data.email,
        street_line=guest_data.street_line,
        plot_number=guest_data.plot_number,
        city=guest_data.city,
        state=guest_data.state,
        zip_code=guest_data.zip_code,
    )

    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)
    return new_guest

# === Get Guest User by Phone Number ===
def get_guest_user_by_phone(db: Session, phone_number: str) -> Optional[GuestUser]:
    validate_phone(phone_number)

    guest = db.query(GuestUser).filter(GuestUser.phone_number == phone_number).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest user not found.")

    return guest


def get_guest_user_by_id(db: Session, guest_user_id: UUID):
    guest = db.query(GuestUser).filter(GuestUser.id == str(guest_user_id)).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest user not found")
    return guest



def get_all_guest_users(db: Session) -> List[GuestUser]:
    return db.query(GuestUser).order_by(GuestUser.created_datetime.desc()).all()



def update_guest_user(
    db: Session,
    guest_user_id: str,
    update_data: GuestUserUpdate
) -> GuestUser:
    guest_user = db.query(GuestUser).filter(GuestUser.id == guest_user_id).first()

    if not guest_user:
        raise HTTPException(status_code=404, detail="Guest user not found.")

    # Validate fields if provided
    if update_data.phone_number:
        validate_phone(update_data.phone_number)
    if update_data.email:
        validate_email(update_data.email)

    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(guest_user, field, value)

    db.commit()
    db.refresh(guest_user)

    return guest_user