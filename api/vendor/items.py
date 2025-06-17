import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from schema.vendor.item_schema import ItemCreate, ItemUpdate, ItemOut
from service.vendor.item_service import (
    create_item,
    get_item_by_id,
    get_all_items,
    update_item_by_id,
    delete_item_by_id,
    get_items_by_category_id
)
from config.db.session import get_db
from utils.jwt_handler import get_current_vendor

item_router = APIRouter(tags=["Items"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@item_router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_new_item(
    category_id: str = Form(...),
    item_name: str = Form(...),
    item_price: float = Form(...),
    discount: float = Form(0.0),
    final_price: Optional[float] = Form(None),  # ✅ New
    kg: float = Form(...),
    quality: str = Form(...),
    quantity: int = Form(...),
    description: Optional[str] = Form(None),    # ✅ New
    additional_images: Optional[List[UploadFile]] = File(None),  # ✅ Accept multiple files
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor) 
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload image.") from e

    images_list = []
    if additional_images:
        for img_file in additional_images:
            if not img_file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="All additional files must be images.")
            img_path = os.path.join(UPLOAD_DIR, img_file.filename)
            with open(img_path, "wb") as buffer:
                shutil.copyfileobj(img_file.file, buffer)
            images_list.append(img_path)
        if len(images_list) > 6:
            raise HTTPException(status_code=400, detail="You can upload a maximum of 6 additional images.")

    item_data = ItemCreate(
        category_id=category_id,
        item_name=item_name.strip(),
        item_price=item_price,
        discount=discount,
        final_price=final_price,       # ✅ Included
        kg=kg,
        quality=quality,
        quantity=quantity,
        description=description,       # ✅ Included
        product_image=file_location,
        additional_images=images_list  # ✅ Included
    )

    try:
        return create_item(item_data, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@item_router.get("/{item_id}", response_model=ItemOut, status_code=status.HTTP_200_OK)
def get_item(item_id: str, db: Session = Depends(get_db)):
    try:
        return get_item_by_id(item_id, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@item_router.get("/", response_model=List[ItemOut], status_code=status.HTTP_200_OK)
def list_items(db: Session = Depends(get_db)):
    return get_all_items(db)



@item_router.put("/{item_id}", response_model=ItemOut, status_code=status.HTTP_200_OK)
async def update_item(
    item_id: str,
    category_id: Optional[str] = Form(None),
    item_name: Optional[str] = Form(None),
    item_price: Optional[float] = Form(None),
    discount: Optional[float] = Form(None),
    final_price: Optional[float] = Form(None),     # ✅ New
    kg: Optional[float] = Form(None),
    quality: Optional[str] = Form(None),
    quantity: Optional[int] = Form(None),
    description: Optional[str] = Form(None),       # ✅ New
    additional_images: Optional[List[UploadFile]] = File(None),  # ✅ Accept multiple files
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor) 
):
    update_data = {}
    if category_id is not None:
        update_data["category_id"] = category_id
    if item_name is not None:
        update_data["item_name"] = item_name.strip()
    if item_price is not None:
        update_data["item_price"] = item_price
    if discount is not None:
        update_data["discount"] = discount
    if final_price is not None:
        update_data["final_price"] = final_price  # ✅ Included
    if kg is not None:
        update_data["kg"] = kg
    if quality is not None:
        update_data["quality"] = quality
    if quantity is not None:
        update_data["quantity"] = quantity
    if description is not None:
        update_data["description"] = description

    # ✅ Save additional image files
    if additional_images is not None:
        images_list = []
        for img_file in additional_images:
            if not img_file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="All additional files must be images.")
            img_path = os.path.join(UPLOAD_DIR, img_file.filename)
            with open(img_path, "wb") as buffer:
                shutil.copyfileobj(img_file.file, buffer)
            images_list.append(img_path)
        if len(images_list) > 6:
            raise HTTPException(status_code=400, detail="You can upload a maximum of 6 additional images.")
        update_data["additional_images"] = images_list

    if file is not None:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to upload image.") from e
        update_data["product_image"] = file_location

    item_update = ItemUpdate(**update_data)

    try:
        return update_item_by_id(item_id, item_update, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@item_router.delete("/{item_id}", status_code=status.HTTP_200_OK, )
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)):
    try:
        return delete_item_by_id(item_id, db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@item_router.get("/items/by-category/{category_id}", response_model=List[ItemOut])
def get_items_by_category(category_id: str, session: Session = Depends(get_db)):
    return get_items_by_category_id(category_id, session)
