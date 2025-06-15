
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.models import Roles
from app.core.error_logger import create_error_response
from app.orders import schemas
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.deps import get_db
from app.auth.dependencies import get_current_user, require_role
from app.cart import models as cart_models
from app.products import models as product_models
from app.orders import models as order_models



router = APIRouter(prefix="/checkout",tags = ["Checkout"])

# Checkout route for users to place an order
@router.post ("",response_model = schemas.OrderOut)
async def checkout(
    data: schemas.CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user)) # role check for users
):
    logger.info(f"Checkout process started by user ID: {current_user['id']}")
    cart_items = db.query(cart_models.Cart).filter(cart_models.Cart.user_id == current_user["id"]).all()

    if not cart_items:
        logger.warning(f"Checkout failed: Cart is empty for user ID {current_user['id']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Cart is empty", "code": 400}
        )

    try:
        total = 0
        order_items = []

        for item in cart_items:
            product = db.query(product_models.Product).filter(product_models.Product.id == item.product_id).first()
            if not product:
                logger.warning(f"Product not found: Product ID {item.product_id} for user ID {current_user['id']}")
                return HTTPException(
                    status_code=404,
                    detail={"error": True, "message": "Product not found", "code": 404}
                )
            
            if product.stock<item.quantity:
                 logger.warning(
                       f"Insufficient stock for Product ID {item.product_id} — "
                       f"Requested: {item.quantity}, Available: {product.stock} — User ID: {current_user['id']}"
                 )
                 return create_error_response(
                      message="Insufficient stock, could not add the product",
                      status_code=status.HTTP_400_BAD_REQUEST
                   )
            product.stock -=item.quantity
            subtotal = product.price * item.quantity
            total += subtotal
            order_items.append(
                order_models.OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=product.price
                )
            )

        # Create order
        order = order_models.Order(user_id=current_user["id"], total_amount=total, status=data.status)
        db.add(order)
        db.flush()  # Get order.id before adding items

        for item in order_items:
            item.order_id = order.id
            db.add(item)

        # Clear cart
        db.query(cart_models.Cart).filter(cart_models.Cart.user_id == current_user["id"]).delete()
        db.commit()
        db.refresh(order)

        logger.info(f"Order placed successfully: Order ID {order.id} by user ID {current_user['id']}")
        return order

    except Exception:
        logger.exception(f"Checkout failed for user ID {current_user['id']}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
   

        

   
  