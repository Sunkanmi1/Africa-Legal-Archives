import random

from fastapi import APIRouter, HTTPException, Query

from models import CaseResult
from services.popularity import case_popularity
from services.wikidata_service import WikidataService

router = APIRouter()
wikidata_service = WikidataService()


@router.get("/api/trending", response_model=list[CaseResult])
async def get_trending_cases(
    country: str = Query("ghana", description="Country code"),
    limit: int = Query(4, ge=1, le=20),
):
    country_key = country.lower().strip()
    if not wikidata_service.is_valid_country(country_key):
        raise HTTPException(status_code=400, detail=f"Unsupported country: {country}")

    cases = await wikidata_service.fetch_cases(country_key)
    counts = case_popularity.ranked_ids()
    ranked = sorted(
        (case for case in cases if counts.get(case.case_id, 0) > 0),
        key=lambda case: (counts[case.case_id], case.case_id),
        reverse=True,
    )
    if ranked:
        return ranked[:limit]

    sample_size = min(limit, len(cases))
    return random.SystemRandom().sample(cases, sample_size) if sample_size else []