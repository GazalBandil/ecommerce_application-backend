
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.models import Roles
from app.orders import schemas
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.auth.dependencies import get_current_user, require_role
from app.cart import models as cart_models
from app.products import models as product_models
from app.orders import models as order_models


router = APIRouter(prefix="/checkout",tags = ["Checkout"])

# Checkout route for users to place an order
@router.post ("",response_model = schemas.OrderOut)
def checkout(
    data: schemas.CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user)) # role check for users
):
    
    cart_items = db.query(cart_models.Cart).filter(cart_models.Cart.user_id == current_user["id"]).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": True, "message": "Cart is empty", "code": 400}
        )

    total = 0
    order_items = []
    for item in cart_items:
        product = db.query(product_models.Product).filter(product_models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail={"error": True, "message": "Product not found", "code": 404})
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
    db.flush()  # To get order.id before adding items

    for item in order_items:
        item.order_id = order.id
        db.add(item)

    # Clear cart
    db.query(cart_models.Cart).filter(cart_models.Cart.user_id == current_user["id"]).delete()
    db.commit()
    db.refresh(order)
    return order
   
  