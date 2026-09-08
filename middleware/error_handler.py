import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

def setup_error_handlers(app: FastAPI) -> None:
    """Registering global exception handlers on the app"""
    @app.exception_handler(HTTPException)
    async def exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail},
        )


    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")

        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal Server Error"},
        )