from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from models.vendor.items import Item
from models.vendor.category import Category  # ✅ Make sure this import exists
from schema.vendor.item_schema import ItemCreate, ItemUpdate
import logging
import uuid

logger = logging.getLogger(__name__)


def create_item(item_data: ItemCreate, session: Session):
    if not item_data.item_name.strip():
        raise HTTPException(status_code=400, detail="Item name cannot be empty")

    # CASE HANDLING FOR FINAL PRICE AND DISCOUNT
    item_price = item_data.item_price
    discount = item_data.discount
    final_price = None

    if discount is not None:
        # Case 1: Discount % given → calculate final price
        final_price = item_price - (item_price * discount / 100)
    elif getattr(item_data, "final_price", None) is not None:
        # Case 2: Final price given → calculate discount %
        final_price = item_data.final_price
        discount = round((1 - final_price / item_price) * 100, 2)
    else:
        # Case 3: Neither discount nor final price → final_price = item_price
        final_price = item_price
        discount = None  # Explicitly set to None for clarity

    new_item = Item(
        id=str(uuid.uuid4()),
        category_id=item_data.category_id,
        item_name=item_data.item_name.strip(),
        item_price=item_price,
        discount=discount,
        final_price=final_price,
        kg=item_data.kg,
        quality=item_data.quality,
        product_image=item_data.product_image,
        quantity=item_data.quantity,
        description=item_data.description,
        additional_images=item_data.additional_images  # ✅ New field included
    )

    try:
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        logger.info(f"Item created: {new_item.id}")
        return new_item
    except IntegrityError:
        session.rollback()
        logger.error("Item creation failed due to integrity error.")
        raise HTTPException(
            status_code=400,
            detail="Failed to create item. Check that the provided category ID is valid and data is not duplicated."
        )


def update_item_by_id(item_id: str, item_data: ItemUpdate, session: Session):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_data.dict(exclude_unset=True)

    # If price and discount are provided, calculate final price
    item_price = update_data.get("item_price", item.item_price)
    discount = update_data.get("discount", item.discount)

    # Automatically calculate final_price if either item_price or discount changes
    if "item_price" in update_data or "discount" in update_data:
        final_price = item_price - ((item_price * discount) / 100)
        update_data["final_price"] = round(final_price, 2)  # Rounded to 2 decimal places

    for key, value in update_data.items():
        setattr(item, key, value)

    logger.info(f"🛠️ Incoming data: {item_data.dict()}")
    logger.info(f"💾 Updating item: {item.item_name}, {item.item_price}, {item.discount}")

    session.commit()
    session.refresh(item)
    logger.info(f"✅ Item updated: {item.id}")
    return item


def get_item_by_id(item_id: str, session: Session):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


def get_all_items(db: Session):
    return db.query(Item).all()  # Remove .offset(skip).limit(limit)



def delete_item_by_id(item_id: str, session: Session):
    item = session.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)
    session.commit()
    logger.info(f"Item deleted: {item_id}")
    return {"message": "Item deleted successfully"}


def get_items_by_category_id(category_id: str, session: Session):
    items = session.query(Item).filter(Item.category_id == category_id).all()
    return items
