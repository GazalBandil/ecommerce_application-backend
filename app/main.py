
from fastapi import FastAPI
from app.core.database import engine ,Base  # Assuming get_db is defined in your database module
from app.auth import models as auth_models
from app.products import models as product_models 



# Importing all the routes
from app.auth.routes import router as auth_router
from app.products.routes import router as product_router

app = FastAPI()

# For creating the database tables
_ = [auth_models , product_models]  
Base.metadata.create_all(bind=engine)  # Create database tables


# Include the authentication routes
app.include_router(auth_router)
app.include_router(product_router)





@app.get("/")
def root():
    return {"api" : "api is running"}


