from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schema.vendor.category_schema import CategoryCreate, CategoryUpdate, CategoryOut, CategoryWithItemsOut
from service.vendor.category_service import (
    create_category,
    get_category_by_id,
    get_all_categories,
    update_category_by_id,
    delete_category_by_id,
    get_all_categories_with_items,
    get_items_by_category_id
)
from config.db.session import get_db
from utils.jwt_handler import get_current_vendor 

category_router = APIRouter(tags=["Categories"])

@category_router.get("/with-items", response_model=list[CategoryWithItemsOut], status_code=status.HTTP_200_OK)
def get_categories_with_items(db: Session = Depends(get_db)):
    return get_all_categories_with_items(db)

@category_router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor protected
):
    try:
        return create_category(category_data, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
@category_router.get("/", response_model=list[CategoryOut], status_code=status.HTTP_200_OK)
def list_categories(db: Session = Depends(get_db)):
    return get_all_categories(db)


@category_router.get("/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
def get_category(category_id: str, db: Session = Depends(get_db)):
    try:
        return get_category_by_id(category_id, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@category_router.put("/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor protected
):
    try:
        return update_category_by_id(category_id, category_data, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@category_router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # 🔐 Vendor protected
):
    try:
        return delete_category_by_id(category_id, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@category_router.get("/{category_id}/items", status_code=status.HTTP_200_OK)
def get_items_for_category(category_id: str, db: Session = Depends(get_db)):
    try:
        return get_items_by_category_id(category_id, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)