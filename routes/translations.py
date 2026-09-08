import logging
from fastapi import APIRouter, HTTPException, Query
from services.wikidata_service import WikidataService

logger = logging.getLogger(__name__)
router = APIRouter()


wikidata_service = WikidataService()


@router.get("/api/translations")
async def get_translations(country: str = Query("ghana", description="Country code"),):
    """Getting available translations for all cases"""
    try:
        country = country.lower().strip()
        if not wikidata_service.is_valid_country(country):
            raise HTTPException(status_code=400, detail="Unsupported country")

        translations = await wikidata_service.fetch_translations(country)
        return {
            "success": True,
            "total_cases": len(translations) if translations else 0,
            "results": translations or [],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch translation data")


@router.get("/api/translations/{case_id}")
async def get_case_translation(case_id: str, country: str = Query("ghana", description="Country code"),):
    """Getting translation for a single case"""
    try:
        country = country.lower().strip()
        if not wikidata_service.is_valid_country(country):
            raise HTTPException(status_code=400, detail=f"Unsupported country: {country}")
        translation = await wikidata_service.fetch_translations(country, case_id)
        if not translation:
            raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

        return {
            "success": True,
            "result": translation
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch translation data")