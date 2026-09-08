import datetime
import logging
import random

from fastapi import APIRouter, HTTPException, Query

from models import CaseResult
from services.wikidata_service import WikidataService
from services.wikisource_service import WikisourceService

logger = logging.getLogger(__name__)
router = APIRouter()

wikidata_service = WikidataService()
wikisource_service = WikisourceService()


@router.get("/api/case-of-the-day")
async def case_of_day(country: str = Query("ghana", description="Country code"),):
    try:
        country = country.lower().strip()
        if not wikidata_service.is_valid_country(country):
            raise HTTPException(status_code=400, detail=f"Unsupported country: {country}")

        cases = await wikidata_service.fetch_cases(country)
        if not cases:
            raise HTTPException(status_code=404, detail=f"No case available")

        # Keep the selection stable for each ten-minute window while allowing
        # it to change automatically without a scheduler or restart.
        window = int(datetime.datetime.now(datetime.UTC).timestamp() // 600)
        selected_case = random.Random(window).choice(cases)

        enriched = await wikisource_service.enrich_case([selected_case])

        return enriched[0] if enriched else selected_case
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error day: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to to fetch case")
