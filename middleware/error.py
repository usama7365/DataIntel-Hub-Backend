from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from jose import JWTError
from pymongo.errors import DuplicateKeyError
from typing import Union

class ErrorHandler(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global error handler for FastAPI
    """
    status_code = 500
    message = "Internal server error"
    
    if isinstance(exc, ErrorHandler):
        status_code = exc.status_code
        message = exc.message
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    elif isinstance(exc, DuplicateKeyError):
        status_code = 400
        message = f"Duplicate {list(exc.details.get('keyValue', {}).keys())} entered"
    elif isinstance(exc, JWTError):
        status_code = 400
        message = "Json Web Token is Invalid, Try again"
    elif hasattr(exc, 'name') and exc.name == "TokenExpiredError":
        status_code = 400
        message = "Json Web Token is Expired, Try again"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message
        }
    )

def handle_validation_error(exc: Exception) -> JSONResponse:
    """
    Handle Pydantic validation errors
    """
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "details": str(exc)
        }
    ) 