from pydantic import BaseModel, Field
from typing import List, Annotated
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class OrderItemOut(BaseModel):
    product_id: int
    quantity: Annotated[int, Field(gt=0, description="Quantity must be greater than 0")]
    price_at_purchase: Annotated[float, Field(gt=0, description="Price must be greater than 0")]

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True

class OrderSummary(BaseModel):
    id: int
    created_at: datetime
    total_amount: float
    status: OrderStatus

    class Config:
        orm_mode = True

class CheckoutRequest(BaseModel):
    status: OrderStatus = OrderStatus.pending