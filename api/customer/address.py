from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db.session import get_db
from schema.customer.address import AddressCreate, AddressUpdate, AddressResponse
from service.customer.address import create_address, update_address, get_addresses_by_customer

address_router = APIRouter(

)

@address_router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address_api(request: AddressCreate, db: Session = Depends(get_db)):
    return create_address(request, db)


@address_router.put("/{address_id}", response_model=AddressResponse)
def update_address_api(address_id: str, request: AddressUpdate, db: Session = Depends(get_db)):
    return update_address(address_id, request, db)


@address_router.get("/customer/{customer_id}", response_model=list[AddressResponse])
def get_addresses_by_customer_api(customer_id: str, db: Session = Depends(get_db)):
    return get_addresses_by_customer(customer_id, db)
