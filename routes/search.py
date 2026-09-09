import logging
from fastapi import APIRouter, HTTPException, Query
import math
from services.wikidata_service import WikidataService
from services.wikisource_service import WikisourceService
from services.popularity import case_popularity
from models import SearchResponse


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/search", response_model=SearchResponse)
async def search_cases(
    country: str = Query("ghana", description="Country code"),
    q: str = Query("", description="Search text query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    year: int | None = Query(None, ge=1000, le=2100),
    judge: str | None = Query(None),
    court: str | None = Query(None),
    citation: str | None = Query(None),
    court_level: str | None = Query(None, pattern="^(supreme|high)$"),
    has_full_text: bool | None = Query(None),
    data_complete: bool | None = Query(None),
):
    """Search for cases based on a query."""
    try:
        country_key = country.lower().strip()
        user_query = q.lower().strip() if q else ""
        wikidata_service = WikidataService()
        if not wikidata_service.is_valid_country(country_key):
            raise HTTPException(status_code=400, detail=f"Unsupported country: {country}")

        logger.info(f"Searching cases - Country: {country_key}")
        cases = await wikidata_service.fetch_cases(country_key)
        if user_query:
            filtered_cases = [
                case for case in cases
                if any(user_query in field.lower()
                    for field in [
                        case.title,
                        case.description,
                        case.court,
                        case.citation,
                        ", ".join([j.name for j in case.judges]),
                    ]
                )
            ]
        else:
            filtered_cases = cases

        if year is not None:
            filtered_cases = [case for case in filtered_cases if case.date.startswith(str(year))]
        if judge:
            filtered_cases = [case for case in filtered_cases if any(judge.lower() in item.name.lower() for item in case.judges)]
        if court:
            filtered_cases = [case for case in filtered_cases if court.lower() in case.court.lower()]
        if citation:
            filtered_cases = [case for case in filtered_cases if citation.lower() in case.citation.lower()]
        if court_level:
            filtered_cases = [case for case in filtered_cases if case.court_level == court_level]
        if data_complete is not None:
            filtered_cases = [case for case in filtered_cases if all([
                case.case_id, case.title, case.date != "Date not recorded",
                case.citation != "Citation not available", case.judges,
            ]) is data_complete]

        if user_query and filtered_cases:
            case_popularity.record(filtered_cases)

        if has_full_text is not None:
            filtered_cases = await WikisourceService().enrich_case(filtered_cases)
            filtered_cases = [case for case in filtered_cases if bool(case.full_text) is has_full_text]

        total_results = len(filtered_cases)
        start = (page - 1) * page_size
        paged_cases = filtered_cases[start:start + page_size]
        enhanced_cases = paged_cases

        return SearchResponse(
            success=True,
            results=enhanced_cases,
            total_results=total_results,
            page=page,
            page_size=page_size,
            total_pages=max(1, math.ceil(total_results / page_size)),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during search for query '{q}': {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
