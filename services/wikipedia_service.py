import asyncio
import httpx

from config import settings
from services.reliability import get_cached, set_cached, with_retries


class WikipediaService:
    endpoint = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "WikiLegalAfrica/1.0 (https://github.com/WikiLegalAfrica)"}

    async def find_article_by_qid(self, wikidata_id: str) -> dict[str, str | None]:
        cache_key = ("wikipedia-judge-qid", wikidata_id)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        async def request():
            async with httpx.AsyncClient(timeout=settings.WIKIDATA_TIMEOUT) as client:
                response = await client.get(
                    "https://www.wikidata.org/w/api.php",
                    params={
                        "action": "wbgetentities",
                        "ids": wikidata_id,
                        "props": "sitelinks",
                        "sitefilter": "enwiki",
                        "format": "json",
                    },
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()

        try:
            data = await with_retries(request)
            entity = data.get("entities", {}).get(wikidata_id, {})
            title = entity.get("sitelinks", {}).get("enwiki", {}).get("title")
            value = {
                "title": title,
                "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}" if title else None,
            }
            return set_cached(cache_key, value)
        except Exception:
            return {"title": None, "url": None}

    async def find_article(self, name: str) -> dict[str, str | None]:
        cache_key = ("wikipedia-judge", name)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        async def request():
            async with httpx.AsyncClient(timeout=settings.WIKIDATA_TIMEOUT) as client:
                response = await client.get(
                    self.endpoint,
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": name,
                        "srnamespace": 0,
                        "srlimit": 1,
                        "format": "json",
                    },
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()

        try:
            data = await with_retries(request)
            result = data.get("query", {}).get("search", [])
            article = result[0].get("title") if result else None
            value = {
                "title": article,
                "url": f"https://en.wikipedia.org/wiki/{article.replace(' ', '_')}" if article else None,
            }
            return set_cached(cache_key, value)
        except Exception:
            return {"title": None, "url": None}

    async def enrich_judges(self, judges: list[dict[str, str | None]]) -> list[dict]:
        results = await asyncio.gather(
            *(self.find_article_by_qid(judge["wikidata_id"]) for judge in judges)
        )
        return [
            {
                "name": judge["name"],
                "wikipedia_title": article["title"],
                "wikipedia_url": article["url"],
            }
            for judge, article in zip(judges, results)
        ]
