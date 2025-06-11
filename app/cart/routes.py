from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.cart import models, schemas
from app.products.models import Product
from app.core.deps import get_db
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

# Add to Cart
@router.post("", response_model=schemas.CartItemOut)
def add_to_cart(
    item: schemas.CartAdd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token or user not found")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    cart_item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == item.product_id
    ).first()

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = models.Cart(
            user_id=user_id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


# View Cart
@router.get("", response_model=List[schemas.CartItemOut])
def view_cart(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("id")
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user_id).all()
    return cart_items


# Remove from Cart
@router.delete("/{product_id}")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("id")
    cart_item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


# Update Quantity
@router.put("/{product_id}", response_model=schemas.CartItemOut)
def update_cart(
    product_id: int,
    item: schemas.CartUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("id")
    cart_item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    cart_item.quantity = item.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item
