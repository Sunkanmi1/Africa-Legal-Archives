import logging
from typing import List, Optional
import httpx
from config import settings
from models import MediaItem
from services.reliability import get_cached, set_cached, with_retries

logger = logging.getLogger(__name__)

JUDGES_CATEGORY = "Category:Justices of the Supreme Court of Ghana"


class CommonsService:
    """Service to enrich case data with information from Wikimedia Commons."""

    def __init__(self):
        self.api_endpoint = settings.COMMONS_API_ENDPOINT
        self.timeout = settings.COMMONS_TIMEOUT
        self.category = "Category:Supreme Court of Ghana building"
        self.headers = {"User-Agent": "WikiLegalAfrica/1.0 (https://github.com/WikiLegalAfrica)"}

    async def search_media(self, query: str, limit: int = 2) -> List[MediaItem]:
        """Search for media items on Wikimedia Commons based on a query."""
        try:
            cache_key = ("commons-media", query, limit)
            cached = get_cached(cache_key)
            if cached is not None:
                return cached

            async def request():
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        self.api_endpoint,
                        params={
                            "action": "query",
                            "list": "search",
                            "srsearch": f"{query} filetype:jpg|png|svg|bitmap",
                            "srnamespace": 6,
                            "format": "json",
                            "srlimit": limit,
                        },
                    )
                    response.raise_for_status()
                    return response.json()

            search_data = await with_retries(request)
            results = search_data.get("query", {}).get("search", [])
            items: List[MediaItem] = []
            for result in results:
                title = result.get("title")
                detail = await self._fetch_image_info(title)
                if detail:
                    items.append(detail)
            return set_cached(cache_key, items)
        except Exception as e:
            logger.warning(f"Error searching Commons for query '{query}': {e}")
            return []

    async def category_media(self, category: str | None = None, limit: int = 3) -> List[MediaItem]:
        category_name = category or self.category
        cache_key = ("commons-category", category_name, limit)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached
        try:
            async def request(continue_params: dict[str, str] | None = None):
                params = {
                    "action": "query",
                    "list": "categorymembers",
                    "cmtitle": category_name,
                    "cmnamespace": 6,
                    "cmlimit": min(limit, 500),
                    "format": "json",
                }
                if continue_params:
                    params.update(continue_params)
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        self.api_endpoint,
                        params=params,
                        headers=self.headers,
                    )
                    response.raise_for_status()
                    return response.json()

            members = []
            continue_params = None
            while len(members) < limit:
                data = await with_retries(lambda: request(continue_params))
                members.extend(data.get("query", {}).get("categorymembers", []))
                continuation = data.get("continue")
                if not continuation:
                    break
                continue_params = {
                    key: value for key, value in continuation.items() if key != "continue"
                }

            members = members[:limit]
            items: List[MediaItem] = []
            for member in members:
                detail = await self._fetch_image_info(member.get("title", ""), category_name)
                if detail:
                    items.append(detail)
            return set_cached(cache_key, items)
        except Exception as e:
            logger.warning(f"Error reading Commons category '{category_name}': {e}")
            return []


    async def _fetch_image_info(self, title: str, category: str | None = None) -> Optional[MediaItem]:
        try:
            async def request():
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        self.api_endpoint,
                        params={
                            "action": "query",
                            "titles": title,
                            "prop": "imageinfo",
                            "iiprop": "url|extmetadata",
                            "iiurlwidth": 400,
                            "format": "json",
                        },
                        headers=self.headers,
                    )
                    response.raise_for_status()
                    return response.json()

            data = await with_retries(request)
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    return None
                imageinfo = page_data.get("imageinfo", [])
                if not imageinfo:
                    return None
                info = imageinfo[0]
                extmetadata = info.get("extmetadata", {})
                description = extmetadata.get("ImageDescription", {}).get("value", "")

                full_url = info.get("url", "")
                thumbnail = info.get("thumburl") or info.get("thumbnail", {}).get("source") or full_url
                license_name = extmetadata.get("LicenseShortName", {}).get("value")
                return MediaItem(
                    title=title.replace("File:", ""),
                    thumbnail_url=thumbnail,
                    full_url=full_url,
                    description=description,
                    source_page=f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
                    license=license_name,
                    category=category,
                )

            return None

        except Exception as e:
            logger.warning(f"Error fetching image info for title '{title}': {e}")
        return None