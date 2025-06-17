from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from models.vendor.category import Category
from models.vendor.category import Category
from schema.vendor.category_schema import CategoryCreate, CategoryUpdate
import logging
import uuid

logger = logging.getLogger(__name__)


def create_category(category_data: CategoryCreate, session: Session):
    if not category_data.category_name.strip():
        raise HTTPException(status_code=400, detail="Category name cannot be empty")

    new_category = Category(
        id=str(uuid.uuid4()),
        vendor_id=category_data.vendor_id,
        category_name=category_data.category_name.strip()
    )

    try:
        session.add(new_category)
        session.commit()
        session.refresh(new_category)
        logger.info(f"Category created: {new_category.id}")
        return new_category
    except IntegrityError:
        session.rollback()
        logger.error("Category creation failed due to integrity error.")
        raise HTTPException(status_code=400, detail="Failed to create category. Possible duplicate or invalid vendor ID.")


def get_category_by_id(category_id: str, session: Session):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def get_all_categories(session: Session):
    return session.query(Category).all()

def update_category_by_id(category_id: str, category_data: CategoryUpdate, session: Session):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category_data.dict(exclude_unset=True).items():
        setattr(category, key, value)

    session.commit()
    session.refresh(category)
    logger.info(f"Category updated: {category.id}")
    return category


def delete_category_by_id(category_id: str, session: Session):
    category = session.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    logger.info(f"Category deleted: {category_id}")
    return {"message": "Category deleted successfully"}



def get_all_categories_with_items(session: Session):
    return session.query(Category).options(joinedload(Category.items)).all()

def get_items_by_category_id(category_id: str, session: Session):
    category = session.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Assuming `Category` model has a relationship like: items = relationship("Item", back_populates="category")
    return {
        "category_id": category.id,
        "category_name": category.category_name,
        "items": category.items  # List of item objects
    }