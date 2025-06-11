from fastapi import APIRouter, Depends, HTTPException, Query, logger
from sqlalchemy.orm import Session
from app.auth.dependencies import require_role
from app.auth.models import Roles
from app.core.deps import get_db
from app.products.models import Product
from app.products.schemas import *


router = APIRouter(prefix='/admin/products', tags=["Admin Products"])

# Post request for products
@router.post("" , response_model = ProductOut , status_code = 201)
async def create_products( 
    product:ProductCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin))
    ):
    exist_product = db.query(Product).filter(Product.name == product.name).first()
    if exist_product:
        raise HTTPException(status_code=400, detail="Product already exists")
    
    new_product = Product(
        name = product.name,
        description = product.description,
        price = product.price,
        stock = product.stock,
        category = product.category,
        image_url=str(product.image_url) if product.image_url else None
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

#  Get all products include pagination
@router.get("", response_model=list[ProductOut],status_code=200)
async def get_all_products(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin)),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    products = db.query(Product).offset(skip).limit(limit).all()
    return [ProductOut.model_validate(p, from_attributes=True) for p in products]


# get products by id aapi 
@router.get("/{id}", response_model=ProductOut)
async def get_product_by_id(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin))
    ):

    product_exists = db.query(Product).filter(Product.id == id).first()
    if not product_exists:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductOut.model_validate(product_exists, from_attributes=True)



# update product 
@router.put("/{id}", response_model=ProductOut)
async def update_product(
    id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin))
):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = product_update.name if product_update.name else product.name
    product.description = product_update.description if product_update.description else product.description
    product.price = product_update.price if product_update.price is not None else product.price
    product.stock = product_update.stock if product_update.stock is not None else product.stock
    product.category = product_update.category if product_update.category else product.category
    product.image_url = str(product_update.image_url) if product_update.image_url else product.image_url
    db.commit()
    db.refresh(product)
    return product

# delete product
@router.delete("/{id}")
async def delete_product(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin))
):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": f"Product '{product.name}' deleted successfully"}


