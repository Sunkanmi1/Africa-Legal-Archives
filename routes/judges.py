from collections import Counter

from fastapi import APIRouter, Query

from models import JudgeProfile
from services.commons_service import CommonsService, JUDGES_CATEGORY
from services.wikidata_service import WikidataService
from services.wikipedia_service import WikipediaService

router = APIRouter()


@router.get("/api/judges", response_model=list[JudgeProfile])
async def get_judges(limit: int = Query(30, ge=1, le=100)):
    cases = await WikidataService().fetch_cases("ghana")
    counts = Counter(judge.name for case in cases for judge in case.judges if judge.name != "Judges unavailable")
    names = [name for name, _ in counts.most_common(limit)]
    profiles = await WikipediaService().enrich_judges(names)
    media = await CommonsService().category_media(category=JUDGES_CATEGORY, limit=limit)

    def media_for_judge(name: str):
        normalized_name = " ".join(name.lower().split())
        matching = [
            item for item in media
            if normalized_name in " ".join(item.title.lower().split())
        ]
        return matching[:1]

    return [
        JudgeProfile(
            name=profile["name"],
            case_count=counts[profile["name"]],
            wikipedia_title=profile["wikipedia_title"],
            wikipedia_url=profile["wikipedia_url"],
            media=media_for_judge(profile["name"]),
        )
        for profile in profiles
    ]