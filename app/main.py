
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.core.database import engine ,Base  # Assuming get_db is defined in your database module
from app.auth import models as auth_models
from app.products import models as product_models 
from app.cart import models as cart_models
from app.orders import models as order_models
from app.core.logging import setup_logging
from app.core.error_logger import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
    )
from app.middlewares.access_logger import AccessLoggerMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException



# Importing all the routes
from app.auth.routes import router as auth_router
from app.products.routes import router as product_router
from app.products.public_routes import router as public_product_router
from app.cart.routes import router as cart_router
from app.orders.checkout_routes import router as checkout_router
from app.orders.orders_routes import router as order_router

load_dotenv()  
smtp_host = os.getenv("SMTP_HOST")
smtp_port = int(os.getenv("SMTP_PORT"))
smtp_user = os.getenv("SMTP_USER")
smtp_pass = os.getenv("SMTP_PASS")

setup_logging()  # Set up logging configuration

app = FastAPI()

app.add_middleware(AccessLoggerMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)



# For creating the database tables
_ = [auth_models , product_models,cart_models , order_models] 

Base.metadata.create_all(bind=engine) # Create database tables


# Include the authentication routes
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(public_product_router)
app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(order_router)


@app.get("/")
def root():
    return {"api" : "api is running"}


