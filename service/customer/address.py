from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.customer.address import Address
from models.customer.user import User as CustomerUser
from schema.customer.address import AddressCreate, AddressUpdate, AddressResponse

def create_address(request: AddressCreate, db: Session) -> AddressResponse:
    customer = db.query(CustomerUser).filter(CustomerUser.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    new_address = Address(
        customer_id=request.customer_id,
        address_line=request.address_line,
        city=request.city,
        state=request.state,
        zip_code=request.zip_code,
        extra_details=request.extra_details
    )

    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return AddressResponse(
        id=new_address.id,
        customer_id=new_address.customer_id,
        address_line=new_address.address_line,
        city=new_address.city,
        state=new_address.state,
        zip_code=new_address.zip_code,
        extra_details=new_address.extra_details,
        created_datetime=new_address.created_datetime,
        updated_datetime=new_address.updated_datetime
    )

def update_address(address_id: str, request: AddressUpdate, db: Session) -> AddressResponse:
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    address.address_line = request.address_line
    address.city = request.city
    address.state = request.state
    address.zip_code = request.zip_code
    address.extra_details = request.extra_details

    db.commit()
    db.refresh(address)

    return AddressResponse(
        id=address.id,
        customer_id=address.customer_id,
        address_line=address.address_line,
        city=address.city,
        state=address.state,
        zip_code=address.zip_code,
        extra_details=address.extra_details,
        created_datetime=address.created_datetime,
        updated_datetime=address.updated_datetime
    )

def get_addresses_by_customer(customer_id: str, db: Session) -> list[AddressResponse]:
    customer = db.query(CustomerUser).filter(CustomerUser.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    addresses = db.query(Address).filter(Address.customer_id == customer_id).all()
    
    return [
        AddressResponse(
            id=addr.id,
            customer_id=addr.customer_id,
            address_line=addr.address_line,
            city=addr.city,
            state=addr.state,
            zip_code=addr.zip_code,
            extra_details=addr.extra_details,
            created_datetime=addr.created_datetime,
            updated_datetime=addr.updated_datetime
        )
        for addr in addresses
    ]