from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    orders = (
        db.query(order_models.Order)
        .filter(order_models.Order.user_id == current_user["id"])
        .order_by(order_models.Order.created_at.desc())
        .all()
    )
    return orders


#view order deatils
@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Roles.user))
):
    order = (
        db.query(order_models.Order)
        .filter(
            order_models.Order.id == order_id,
            order_models.Order.user_id == current_user["id"]
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": True, "message": "Order not found", "code": 404}
        )

    return order
