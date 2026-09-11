from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Server settings
    PORT: int = 3000
    HOST: str = "0.0.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    #URLs
    BASE_URL: str = "http://localhost:3000"
    CORS_ORIGIN: str = "http://localhost:5176"

    #External APIs
    WIKIDATA_ENDPOINT: str = "https://query.wikidata.org/sparql"
    WIKISOURCE_API_ENDPOINT: str = "https://en.wikisource.org/w/api.php?action=visualeditor&mode=viewpage&page=PAGE_TITLE&format=json"
    WIKISOURCE_API: str = WIKISOURCE_API_ENDPOINT
    COMMONS_API_ENDPOINT: str = "https://commons.wikimedia.org/w/api.php"
    COMMONS_API: str = COMMONS_API_ENDPOINT

    #TIMEOUT
    WIKIDATA_TIMEOUT: int = 10
    WIKISOURCE_TIMEOUT: int = 5
    COMMONS_TIMEOUT: int = 5

    #cache
    CACHE_TTL: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> "Settings":
    return Settings()

settings = get_settings()
