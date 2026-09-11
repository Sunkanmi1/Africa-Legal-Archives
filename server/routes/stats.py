import logging
import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from models import StatResponse
from services.wikidata_service import WikidataService

logger = logging.getLogger(__name__)
router = APIRouter()

COUNTRIES = ["ghana"]
wikidata_service = WikidataService()


@router.get("/api/stats", response_model=StatResponse)
async def get_stats():
    try:
        results = await asyncio.gather(
            *(wikidata_service.fetch_cases(country) for country in COUNTRIES),
            return_exceptions=True,
        )
        total_cases = 0
        failed_countries = 0
        for result in results:
            if isinstance(result, Exception):
                failed_countries += 1
                continue
            total_cases += len(result)

        if failed_countries:
            logger.warning("Stats unavailable for %s countries", failed_countries)

        return StatResponse(
            success=True,
            archived_cases=total_cases,
            nations_covered=len(wikidata_service.get_countries()),
            last_update=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute stats")