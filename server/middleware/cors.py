from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

def setup_cors(app: FastAPI) -> None:
    """Registering CORS middleware for the FastAPI app"""
    allowed_origins = [
        settings.CORS_ORIGIN,
        "http://127.0.0.1:5176",
        "https://wikilegalafrica.toolforge.org",
        "http://wikilegalafrica.toolforge.org",

        "https://ghanasupremecases.toolforge.org",
        "http://ghanasupremecases.toolforge.org",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
