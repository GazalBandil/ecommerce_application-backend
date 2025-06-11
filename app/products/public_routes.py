from fastapi import APIRouter, Depends, Query
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.auth.dependencies import get_current_user
from app.core.deps import get_db
from app.products.models import Product
from app.products.schemas import ProductOut


router = APIRouter(prefix='/products', tags=["Public Products"])


# List all products with optional filters and sorting
@router.get("", response_model=List[ProductOut])
async def get_products(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, gt=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum price"),
    sort_by: Optional[str] = Query("price", pattern="^(price|name|stock)$", description="Sort by field"),
    page: int = Query(1, gt=0, description="Page number"),
    page_size: int = Query(10, gt=0, le=100, description="Number of items per page"),
):
    try:
        if sort_by not in ["price", "name", "stock"]:
            raise http_exception_handler("Invalid sort_by value. Choose from: price, name, stock", 400)
        
        query = db.query(Product)

        if category:
            query = query.filter(func.lower(Product.category) == category.lower())
        if min_price:
            query = query.filter(Product.price >= min_price)
        if max_price:
            query = query.filter(Product.price <= max_price)

        query = query.order_by(getattr(Product, sort_by))

        start = (page - 1) * page_size
        products = query.offset(start).limit(page_size).all()

        return products
    except Exception:
        raise http_exception_handler("Unable to retrieve products", 500)
    

# Search for products by keyword
@router.get("/search", response_model=List[ProductOut])
async def search_products(
    keyword: str = Query(..., min_length=1, description="Search term"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        results = db.query(Product).filter(
            Product.name.ilike(f"%{keyword}%") | Product.description.ilike(f"%{keyword}%")
        ).all()
        return results
    except Exception:
        raise http_exception_handler("Search failed", 500)



# Get details of a single product by ID
@router.get("/{id}", response_model=ProductOut)
async def get_product_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        product = db.query(Product).filter(Product.id == id).first()
        if not product:
            raise http_exception_handler(f"Product with ID {id} not found", 404)
        return product
   
    except Exception:
        raise http_exception_handler("Could not retrieve product details", 500)
