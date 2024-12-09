from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

class CustomErrorMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware
    """
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Logging the error 
            print(f"Unhandled exception: {exc}")
            
            # Default error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": str(exc),
                    "request": {
                        "method": request.method,
                        "url": str(request.url)
                    }
                }
            )

def setup_exception_handlers(app):
    """
    Settung up specific exception handlers
    """
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "request": {
                    "method": request.method,
                    "url": str(request.url)
                }
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "detail": str(exc),
                "request": {
                    "method": request.method,
                    "url": str(request.url)
                }
            }
        )