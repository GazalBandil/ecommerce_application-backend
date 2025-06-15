from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger

def create_error_response(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": message,
            "code": status_code
        },
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return create_error_response(exc.detail, exc.status_code)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    return create_error_response("Validation Error", 422)

async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled Exception")
    return create_error_response("Internal Server Error", 500)
