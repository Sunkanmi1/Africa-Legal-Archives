from collections import Counter

from fastapi import APIRouter, Query

from models import JudgeProfile
from services.wikidata_service import WikidataService
from services.wikipedia_service import WikipediaService

router = APIRouter()


@router.get("/api/judges", response_model=list[JudgeProfile])
async def get_judges(limit: int = Query(30, ge=1, le=100)):
    cases = await WikidataService().fetch_cases("ghana")
    judges = {
        judge.wikidata_id: judge
        for case in cases
        for judge in case.judges
        if judge.name != "Judges unavailable" and judge.wikidata_id
    }
    counts = Counter(
        judge.wikidata_id
        for case in cases
        for judge in case.judges
        if judge.name != "Judges unavailable" and judge.wikidata_id
    )
    top_judges = [judges[qid] for qid, _ in counts.most_common(limit)]
    profiles = await WikipediaService().enrich_judges([
        {"name": judge.name, "wikidata_id": judge.wikidata_id}
        for judge in top_judges
    ])

    return [
        JudgeProfile(
            name=profile["name"],
            case_count=counts[top_judges[index].wikidata_id],
            wikipedia_title=profile["wikipedia_title"],
            wikipedia_url=profile["wikipedia_url"],
        )
        for index, profile in enumerate(profiles)
    ]