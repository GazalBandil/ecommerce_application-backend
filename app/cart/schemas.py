from pydantic import BaseModel, Field
from typing import Optional

class CartAdd(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class CartUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True
