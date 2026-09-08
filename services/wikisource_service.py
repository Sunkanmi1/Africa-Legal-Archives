import asyncio
import logging
from typing import List, Optional
import httpx
from config import settings
from models import CaseResult
from services.reliability import get_cached, set_cached, with_retries

logger = logging.getLogger(__name__)

class WikisourceService:
    def __init__(self):
        self.api_endpoint = settings.WIKISOURCE_API_ENDPOINT
        self.timeout = settings.WIKISOURCE_TIMEOUT

    async def enrich_case(self, cases: List[CaseResult]) -> List[CaseResult]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [self._fetch_case_details(case) for case in cases]
            enriched_cases = await asyncio.gather(*tasks, return_exceptions=True)
        return [case for case in enriched_cases if not isinstance(case, Exception)]

    async def _fetch_case_details(self, case: CaseResult) -> CaseResult:
        try:
            search_query = f"{case.title}{case.citation}".strip()
            wikisource_data = await self._search_wikisource(search_query)
            if wikisource_data:
                case.wikisource_url = wikisource_data.get("url")
                case.full_text = wikisource_data.get("full_text")
                case.opinion_summary = wikisource_data.get("summary")
            return case
        except Exception as e:
            logger.warning(f"Error fetching Wikisource details for case {case.case_id}: {e}")
            return case

    async def _search_wikisource(self, query: str) -> Optional[dict]:
        cache_key = ("wikisource-search", query)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached
        try:
            async def request():
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        self.api_endpoint,
                        params={
                            "action": "query",
                            "list": "search",
                            "srsearch": query,
                            "format": "json",
                            "srlimit": 5,
                        },
                    )
                    response.raise_for_status()
                    return response.json()

            search_data = await with_retries(request)
            results = search_data.get("query", {}).get("search", [])
            if not results:
                logger.info(f"No Wikisource results found for query: {query}")
                return None

            page_title = results[0].get("title")
            content = await self._fetch_page_content(page_title)
            if content:
                return set_cached(cache_key, {
                    "url": f"https://en.wikisource.org/wiki/{page_title.replace(' ', '_')}",
                    "full_text": content.get("full_text"),
                    "summary": content.get("summary")
                })
            return None
        except Exception as e:
            logger.error(f"Error searching Wikisource for query '{query}': {e}")
            return None

    async def _fetch_page_content(self, title: str) -> Optional[dict]:
        try:
            async def request():
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        self.api_endpoint,
                        params={
                            "action": "query",
                            "titles": title,
                            "prop": "extracts",
                            "explaintext": True,
                            "format": "json",
                        },
                    )
                    response.raise_for_status()
                    return response.json()

            data = await with_retries(request)
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    return None
                extract = page_data.get("extract", "")
                if extract:
                    summary = (extract[:500] + '...') if len(extract) > 500 else extract
                    return {
                        "full_text": extract,
                        "summary": summary
                    }
                return None
        except Exception as e:
            logger.error(f"Error fetching Wikisource page content for title '{title}': {e}")
            return None