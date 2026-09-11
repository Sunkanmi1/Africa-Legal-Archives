from fastapi import APIRouter
from models import CountriesResponse
from services.wikidata_service import WikidataService

router = APIRouter()
wikidata_service = WikidataService()

@router.get("/api/countries")
async def get_countries():
    """Get list of supported countries : powers sidebar 'Countries' Tab link"""
    countries = wikidata_service.get_countries()
    return CountriesResponse(
        success=True,
        total_countries=len(countries),
        countries=countries,
    )