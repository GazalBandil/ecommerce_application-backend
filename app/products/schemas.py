from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str
    image_url: Optional[HttpUrl] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    

class ProductOut(ProductBase):
    id: int

    model_config = {
        "from_attributes": True
    }