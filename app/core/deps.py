from app.core.database import SessionLocal


# This function provides a database session for dependency injection in FastAPI routes.
# It ensures that the session is properly closed after use.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

