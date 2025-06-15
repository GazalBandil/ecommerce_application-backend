from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.core.error_logger import create_error_response
from app.core.logging import logger
from app.core.deps import get_db
from app.auth.dependencies import require_role
from app.auth.models import Roles
from app.orders import models as order_models, schemas

router = APIRouter(prefix="/orders", tags=["Orders"])

# view order history
@router.get("", response_model=List[schemas.OrderSummary] ,status_code=status.HTTP_200_OK)
def get_order_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user))
):
     
    logger.info(f"Fetching order history for user ID: {current_user['id']}")
    try:
        orders = (
        db.query(order_models.Order)
        .filter(order_models.Order.user_id == current_user["id"])
        .order_by(order_models.Order.created_at.desc())
        .all()
        )
        if not orders:
            logger.warning(f"No orders found for user ID: {current_user['id']} — returning 204 No Content")
            return create_error_response(f"No orders found for user ID: {current_user['id']}" ,status_code=status.HTTP_404_NOT_FOUND)
        else:
            logger.info(f"Found {len(orders)} orders for user ID: {current_user['id']}")

        return orders
    
    except Exception:
        logger.exception(f"Failed to fetch order history for user ID: {current_user['id']}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#view order deatils
@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user))
):
    logger.info(f"Fetching order details: Order ID {order_id} for user ID {current_user['id']}")

    try:
        order = (
            db.query(order_models.Order)
            .filter(
                order_models.Order.id == order_id,
                order_models.Order.user_id == current_user["id"]
            )
            .first()
        )

        if not order:
            logger.warning(f"Order not found: Order ID {order_id} for user ID {current_user['id']}")
            return create_error_response(
                f"Order not found for ID {order_id}",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        logger.info(f"Order details retrieved successfully: Order ID {order_id} for user ID {current_user['id']}")
        return order

    except Exception:
        logger.exception(f"Failed to fetch order details: Order ID {order_id} for user ID {current_user['id']}")
        raise HTTPException(status_code=500, detail="Internal Server Error")