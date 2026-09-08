from collections import Counter

from fastapi import APIRouter

from models import QualityResponse
from services.wikidata_service import WikidataService

router = APIRouter()


@router.get("/api/quality", response_model=QualityResponse)
async def get_quality_report():
    cases = await WikidataService().fetch_cases("ghana")
    counts = Counter(case.case_id for case in cases)
    return QualityResponse(
        success=True,
        total_cases=len(cases),
        duplicate_case_ids=[case_id for case_id, count in counts.items() if count > 1],
        missing_dates=sum(case.date == "Date not recorded" for case in cases),
        missing_citations=sum(case.citation == "Citation not available" for case in cases),
        missing_judges=sum(not case.judges or case.judges[0].name == "Judges unavailable" for case in cases),
        invalid_qids=sum(not case.case_id.startswith("Q") for case in cases),
    )