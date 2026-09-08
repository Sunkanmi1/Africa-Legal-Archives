from fastapi import FastAPI
from middleware.cors import setup_cors
from middleware.error_handler import setup_error_handlers
from routes import health, search, countries, stats, translations, case_of_day, media, cases, quality, judges

app = FastAPI(
    title="WikiLegal Africa API",
    version="0.2.0",
    description="Searchable database of Supreme Court cases accross Africa"
)

setup_cors(app)
setup_error_handlers(app)

app.include_router(health.router)
app.include_router(search.router)
app.include_router(countries.router)
app.include_router(media.router)
app.include_router(stats.router)
app.include_router(translations.router)
app.include_router(case_of_day.router)
app.include_router(cases.router)
app.include_router(quality.router)
app.include_router(judges.router)

if __name__ == "__main__":
    import uvicorn 
    from config import settings

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" 
        if not settings.DEBUG else "debug"
    )