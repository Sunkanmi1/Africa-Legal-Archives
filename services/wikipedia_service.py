import asyncio
import httpx

from config import settings
from services.reliability import get_cached, set_cached, with_retries


class WikipediaService:
    endpoint = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "WikiLegalAfrica/1.0 (https://github.com/WikiLegalAfrica)"}

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

    async def enrich_judges(self, names: list[str]) -> list[dict]:
        results = await asyncio.gather(*(self.find_article(name) for name in names))
        return [
            {"name": name, "wikipedia_title": article["title"], "wikipedia_url": article["url"]}
            for name, article in zip(names, results)
        ]
