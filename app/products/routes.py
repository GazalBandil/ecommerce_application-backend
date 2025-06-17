from fastapi import APIRouter, Depends, HTTPException, Query , status
from app.core.error_logger import create_error_response
from app.core.logging import logger
from sqlalchemy.orm import Session
from app.auth.dependencies import require_role
from app.auth.models import Roles
from app.core.deps import get_db
from app.orders.models import OrderItem
from app.products.models import Product
from app.products.schemas import *


router = APIRouter(prefix='/admin/products', tags=["Admin Products"])


#POST CREATE PRODUCT - accessible to admin only
@router.post("" , response_model = ProductOut , status_code = 201)
async def create_products( 
    product:ProductCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin))
):
 # Check if the product already exists
 exist_product = db.query(Product).filter(Product.name == product.name).first()
 if exist_product:
        logger.warning(f"Product creation failed: '{product.name}' already exists.")
        raise HTTPException(status_code=400, detail="Product already exists")

 try: 
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
    logger.info(f"Product created: ID {product.id} by admin ID: {user.id}")
    return new_product
 
 except Exception as e:
        logger.exception("Error occurred while creating product.")
        raise HTTPException(status_code=500, detail="Internal Server Error")



#GET ALL PRODUCTS- USE OF PAGINATION - accessible to admin only
@router.get("", response_model=list[ProductOut],status_code=200)
async def get_all_products(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin)),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    try:
        products = db.query(Product).offset(skip).limit(limit).all()
        logger.info(
            f"Admin {user['email']} accessed product list: skip={skip}, limit={limit}, total={len(products)}"
        )

        return [ProductOut.model_validate(p, from_attributes=True) for p in products]

    except Exception as e:
        logger.error(f"Failed to fetch products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "message": "Something went wrong while fetching products",
                "code": 500,
            },
        )
    


# GET PRODUCTS BY ID - accessible to admin only
@router.get("/{id}", response_model=ProductOut)
async def get_product_by_id(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin))
    ):

    product_exists = db.query(Product).filter(Product.id == id).first()
    if not product_exists:
        logger.warning(f"Product not found for ID: {id}")
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        logger.info(f"Product fetched successfully: ID={id} by AdminID={user.get('id')}")
        return ProductOut.model_validate(product_exists, from_attributes=True)

    except Exception as e:
        logger.exception(f"Exception while serializing product ID={id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


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
        logger.warning(f"Update failed: Product with ID {id} not found")
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        product.name = product_update.name if product_update.name else product.name
        product.description = product_update.description if product_update.description else product.description
        product.price = product_update.price if product_update.price is not None else product.price
        product.stock = product_update.stock if product_update.stock is not None else product.stock
        product.category = product_update.category if product_update.category else product.category
        product.image_url = str(product_update.image_url) if product_update.image_url else product.image_url

        db.commit()
        db.refresh(product)

        logger.info(f"Product updated: ID={id} by AdminID={user.get('id')}")
        return product

    except Exception as e:
        logger.exception(f"Exception while updating product ID={id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# delete product
@router.delete("/{id}")
async def delete_product(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(Roles.admin))
):
   product = db.query(Product).filter(Product.id == id).first()
   if not product:
        logger.warning(f"Delete failed: Product with ID {id} not found")
        raise HTTPException(status_code=404, detail="Product not found")

   try:
        product_in_orders = db.query(OrderItem).filter(OrderItem.product_id == id).first()
        if product_in_orders:
            logger.warning(f"Delete failed: Product ID {id} is referenced in orders, cannot be deleted")
            return create_error_response(
                f"Product '{product.name}' is part of existing orders and cannot be deleted",
                 status_code=status.HTTP_400_BAD_REQUEST
            )
        db.delete(product)
        db.commit()
        logger.info(f"Product deleted: ID={id}, Name='{product.name}', by AdminID={user.get('id')}")
        return {"message": f"Product '{product.name}' deleted successfully"}
    
   except Exception:
        logger.exception(f"Exception while deleting product ID={id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

