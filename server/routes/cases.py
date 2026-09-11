from fastapi import APIRouter, HTTPException

from models import CaseResult
from services.wikidata_service import WikidataService
from services.wikisource_service import WikisourceService

router = APIRouter()


@router.get("/api/cases/{case_id}", response_model=CaseResult)
async def get_case(case_id: str):
    cases = await WikidataService().fetch_cases("ghana")
    result = next((case for case in cases if case.case_id == case_id), None)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")
    enriched = await WikisourceService().enrich_case([result])
    return enriched[0] if enriched else result