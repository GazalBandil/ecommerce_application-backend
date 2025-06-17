from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.auth.models import Roles
from app.core.error_logger import create_error_response
from app.core.logging import logger
from app.cart import models, schemas
from app.products.models import Product
from app.core.deps import get_db
from app.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/cart", tags=["Cart"])

# Add to Cart
@router.post("", response_model=schemas.CartItemOut)
async def add_to_cart(
    item: schemas.CartAdd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user))
):
    user_id = current_user.get("id")
    if not user_id:
        logger.warning("Add to cart failed: Invalid token or user not found.")
        raise HTTPException(status_code=401, detail="Invalid token or user not found")

    try:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            logger.warning(f"Product not found: Product ID {item.product_id}")
            return create_error_response("Product not found", status_code=status.HTTP_404_NOT_FOUND)

        if product.stock <= 0:
            logger.warning(f"Product stock is{product.stock} not available, by user ID {user_id}")
            return create_error_response("Current product is out of stock" ,status_code=status.HTTP_400_BAD_REQUEST)

        cart_item = db.query(models.Cart).filter(
            models.Cart.user_id == user_id,
            models.Cart.product_id == item.product_id
        ).first()

        if cart_item:
            cart_item.quantity += item.quantity
            logger.info(f"Updated cart: Added {item.quantity} more of product ID {item.product_id} for user ID {user_id}")
        else:
            cart_item = models.Cart(
                user_id=user_id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(cart_item)
            logger.info(f"New cart item added: Product ID {item.product_id} x{item.quantity} for user ID {user_id}")

        db.commit()
        db.refresh(cart_item)
        return cart_item

    except Exception:
        logger.exception(f"Failed to add to cart for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


# View Cart
@router.get("", response_model=List[schemas.CartItemOut])
async def view_cart(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user))
):
    user_id = current_user.get("id")
    logger.info(f"Fetching cart for user ID: {user_id}")

    try:
        cart_items = db.query(models.Cart).filter(models.Cart.user_id == user_id).all()

        if not cart_items:
            logger.warning(f"Cart is empty for user ID: {user_id}")
            return create_error_response(
                "Cart is empty",
                status_code=status.HTTP_204_NO_CONTENT
              
            )

        logger.info(f"Cart contains {len(cart_items)} items for user ID: {user_id}")
        return cart_items

    except Exception:
        logger.exception(f"Failed to fetch cart for user ID: {user_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Remove from Cart
@router.delete("/{product_id}")
async def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user))
):
    user_id = current_user.get("id")
    logger.info(f"Attempting to remove product ID {product_id} from cart for user ID {user_id}")

    try:
        cart_item = db.query(models.Cart).filter(
            models.Cart.user_id == user_id,
            models.Cart.product_id == product_id
        ).first()

        if not cart_item:
            logger.warning(f"Cart item not found: Product ID {product_id} for user ID {user_id}")
            return create_error_response("Cart item not found",status_code=404)

        db.delete(cart_item)
        db.commit()

        logger.info(f"Successfully removed product ID {product_id} from cart for user ID {user_id}")
        return {"message": "Item removed from cart"}

    except Exception:
        logger.exception(f"Error while removing product ID {product_id} from cart for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Update Quantity
@router.put("/{product_id}", response_model=schemas.CartItemOut)
async def update_cart(
    product_id: int,
    item: schemas.CartUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user))
):
    user_id = current_user.get("id")
    logger.info(f"Attempting to update product ID {product_id} in cart for user ID {user_id}")

    try:
        cart_item = db.query(models.Cart).filter(
            models.Cart.user_id == user_id,
            models.Cart.product_id == product_id
        ).first()

        if not cart_item:
            logger.warning(f"Cart item not found: Product ID {product_id} for user ID {user_id}")
            raise HTTPException(status_code=404, detail="Cart item not found")

        if item.quantity <= 0:
            logger.warning(f"Invalid quantity {item.quantity} provided by user ID {user_id} for product ID {product_id}")
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

        cart_item.quantity = item.quantity
        db.commit()
        db.refresh(cart_item)

        logger.info(f"Updated quantity to {item.quantity} for product ID {product_id} in cart of user ID {user_id}")
        return cart_item

    except Exception:
        logger.exception(f"Error while updating product ID {product_id} in cart for user ID {user_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")