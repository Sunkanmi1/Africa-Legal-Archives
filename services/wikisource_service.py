import asyncio
import logging
import re
from typing import List, Optional
from urllib.parse import quote, unquote, urlparse
import httpx
from config import settings
from models import CaseResult
from services.reliability import get_cached, set_cached, with_retries

logger = logging.getLogger(__name__)

PLACEHOLDER_CITATION_PATTERNS = (
    "citation not available",
    "citation unavailable",
    "not available",
    "no citation",
)

class WikisourceService:
    def __init__(self):
        self.api_endpoint = settings.WIKISOURCE_API_ENDPOINT
        self.timeout = settings.WIKISOURCE_TIMEOUT
        self.headers = {
            "User-Agent": "WikiLegalAfrica/1.0 (contact: hello@wikilegal.africa)",
            "Accept": "application/json",
        }
        self.commons_endpoint = settings.COMMONS_API_ENDPOINT

    @staticmethod
    def _file_name_from_url(url: Optional[str]) -> str:
        if not url:
            return ""
        path = unquote(urlparse(url).path)
        if "/File:" in path:
            return path.split("/File:", 1)[1]
        if "/Special:FilePath/" in path:
            return path.split("/Special:FilePath/", 1)[1]
        return ""

    def _build_search_query(self, case: CaseResult) -> str:
        parts = []
        if case.title and case.title.strip():
            parts.append(case.title.strip())
        if case.citation and case.citation.strip():
            citation = case.citation.strip()
            if not any(pattern in citation.lower() for pattern in PLACEHOLDER_CITATION_PATTERNS):
                parts.append(citation)
        query = " ".join(parts)
        query = re.sub(r"\s+", " ", query).strip()
        return query.strip(" -:;,.()[]{}")

    async def enrich_case(self, cases: List[CaseResult]) -> List[CaseResult]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [self._fetch_case_details(case) for case in cases]
            enriched_cases = await asyncio.gather(*tasks, return_exceptions=True)
        return [case for case in enriched_cases if not isinstance(case, Exception)]

    async def _fetch_case_details(self, case: CaseResult) -> CaseResult:
        try:
            file_name = self._file_name_from_url(case.commons_file_url)
            wikisource_data = await self._fetch_document_data(case, file_name) if file_name else None
            if not wikisource_data:
                search_query = self._build_search_query(case)
                if not search_query:
                    return case
                wikisource_data = await self._search_wikisource(search_query)
            if wikisource_data:
                case.wikisource_url = wikisource_data.get("url")
                case.full_text = wikisource_data.get("full_text")
                case.opinion_summary = wikisource_data.get("summary")
                case.commons_preview_url = wikisource_data.get("preview_url")
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
                async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
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

    async def _fetch_document_data(self, case: CaseResult, file_name: str) -> Optional[dict]:
        """Load Commons' first-page preview and Wikisource Page transcriptions for a PDF."""
        cache_key = ("wikisource-document", file_name)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            async def request(params: dict, endpoint: str):
                async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                    response = await client.get(endpoint, params=params)
                    response.raise_for_status()
                    return response.json()

            commons_data = await with_retries(lambda: request({
                "action": "query",
                "titles": f"File:{file_name}",
                "prop": "imageinfo",
                "iiprop": "url|thumburl",
                "iiurlwidth": 900,
                "format": "json",
            }, self.commons_endpoint))
            preview_url = None
            for page_data in commons_data.get("query", {}).get("pages", {}).values():
                image_info = page_data.get("imageinfo", [])
                if image_info:
                    preview_url = image_info[0].get("thumburl")
                    break

            search_data = await with_retries(lambda: request({
                "action": "query",
                "list": "search",
                "srsearch": file_name.rsplit(".", 1)[0],
                "srnamespace": 104,
                "format": "json",
                "srlimit": 50,
            }, self.api_endpoint))
            page_titles = [
                item.get("title")
                for item in search_data.get("query", {}).get("search", [])
                if item.get("title", "").startswith("Page:")
            ]
            if not page_titles and not preview_url:
                return None

            texts = []
            for title in page_titles:
                page_data = await with_retries(lambda title=title: request({
                    "action": "parse",
                    "page": title,
                    "prop": "wikitext",
                    "format": "json",
                }, self.api_endpoint))
                raw_text = page_data.get("parse", {}).get("wikitext", {}).get("*", "")
                cleaned_text = re.sub(r"<noinclude>.*?</noinclude>", "", raw_text, flags=re.DOTALL)
                cleaned_text = re.sub(r"<pagequality[^>]*/>", "", cleaned_text)
                cleaned_text = re.sub(r"\{\{[^{}]+\}\}", "", cleaned_text)
                cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
                if cleaned_text:
                    texts.append(cleaned_text)

            full_text = "\n\n".join(texts) or None
            result = {
                "url": case.wikisource_url or f"https://en.wikisource.org/wiki/Index:{quote(file_name)}",
                "full_text": full_text,
                "summary": ((full_text[:500] + "...") if full_text and len(full_text) > 500 else full_text),
                "preview_url": preview_url,
            }
            return set_cached(cache_key, result)
        except Exception as e:
            logger.warning("Error loading document data for '%s': %s", file_name, e)
            return None

    async def _fetch_page_content(self, title: str) -> Optional[dict]:
        try:
            async def request():
                async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
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