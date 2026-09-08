from datetime import datetime
from fastapi import APIRouter
from config import settings
from models import HealthResponse

router = APIRouter()

@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow().isoformat() + "Z", environment=settings.ENVIRONMENT, version="0.2.0")


@router.get("/")
async def root():
    """Root endpoint for the available endpoints"""
    base_url = settings.BASE_URL
    return {
        "message": "Your guy is up and kicking",
        "version": "0.2.0",
        "endpoints": {
            "health": f"GET {base_url}/api/health"
        }
    }