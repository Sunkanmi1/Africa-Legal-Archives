import asyncio
import logging
from typing import List, Dict, Optional
from urllib.parse import quote, unquote, urlparse
import httpx
from config import settings
from models import CaseResult, Judge
from services.reliability import get_cached, set_cached, with_retries

logger = logging.getLogger(__name__)

COUNTRY_CONFIG = {
    "ghana": {
        "court_id": "Q1513611",
        "high_court_id": "Q141203275",
        "high_court_case_class": "Q141369159",
        "country_id": "Q117",
    },
}

class WikidataService:
    def __init__(self):
        self.endpoint = settings.WIKIDATA_ENDPOINT
        self.timeout = settings.WIKIDATA_TIMEOUT
        self.headers = {
            "User-Agent": "LegalDataApp/1.0 (your_email@example.com)",
            "Accept": "application/sparql-results+json"
        }

    def is_valid_country(self, country: str) -> bool:
        return country.lower() in COUNTRY_CONFIG

    def get_countries(self) -> List[Dict]:
        return [
            {
                "code": code, 
                "name": code.capitalize().replace("_", " "),
                "wikidata_id": config["country_id"],
            }
            for code, config in COUNTRY_CONFIG.items()
        ]

    async def fetch_supreme_court_cases(self, country: str) -> List[CaseResult]:
        country_key = country.lower().strip()
        country_config = COUNTRY_CONFIG.get(country_key)
        if not country_config:
            raise ValueError(f"Unsupported country: {country}")

        cache_key = ("wikidata-supreme-cases", country_key)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        sparql_query = f"""
            SELECT DISTINCT ?item ?itemLabel ?itemDescription ?date ?legal_citation ?courtLabel ?sourceLabel 
            (GROUP_CONCAT(DISTINCT CONCAT(STR(?judge_item), "|", ?judge); separator="||") AS ?judge_data)
            WHERE {{
                {{
                    SELECT DISTINCT ?item ?court WHERE {{
                        ?item (wdt:P31/(wdt:P279*)) wd:Q114079647;
                              (wdt:P17/(wdt:P279*)) wd:{country_config["country_id"]};
                              wdt:P4884 ?court.
                        ?court (wdt:P279*) wd:{country_config["court_id"]}.
                    }}
                    LIMIT 5000
                }}
                
                OPTIONAL {{ ?item wdt:P577 ?date. }}
                OPTIONAL {{ ?item wdt:P1031 ?legal_citation. }}
                OPTIONAL {{ ?item wdt:P1433 ?source. }}
                
                OPTIONAL {{
                    ?item wdt:P1594 ?judge_item. 
                    ?judge_item rdfs:label ?judge. 
                    FILTER(LANG(?judge) = "en") 
                }}
                
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en". }} 
            }} 
            GROUP BY ?item ?itemLabel ?itemDescription ?date ?legal_citation ?courtLabel ?sourceLabel 
            ORDER BY DESC(?date)
        """

        try:
            async def request():
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        self.endpoint,
                        params={"query": sparql_query, "format": "json"},
                        headers=self.headers,
                    )
                    response.raise_for_status()
                    return response.json()

            data = await with_retries(request)

            cases = []
            for binding in data.get("results", {}).get("bindings", []):
                case = self.parse_wikidata_binding(binding, country_key)
                if case:
                    cases.append(case)

            logger.info(f"Fetched {len(cases)} cases from Wikidata for {country}")
            return set_cached(cache_key, cases)
        except Exception as e:
            logger.error(f"Error fetching cases for {country}: {str(e)}")
            raise

    async def fetch_cases(self, country: str) -> List[CaseResult]:
        """Merge the separate Supreme Court and High Court collections by QID."""
        country_key = country.lower().strip()
        if country_key not in COUNTRY_CONFIG:
            raise ValueError(f"Unsupported country: {country}")

        cache_key = ("wikidata-cases", country_key)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        results = await asyncio.gather(
            self.fetch_supreme_court_cases(country_key),
            self.fetch_high_court_cases(country_key),
            return_exceptions=True,
        )
        cases_by_id: Dict[str, CaseResult] = {}
        had_fetch_error = False
        for result in results:
            if isinstance(result, Exception):
                had_fetch_error = True
                logger.warning("A Ghana court collection could not be loaded: %s", result)
                continue
            for case in result:
                cases_by_id.setdefault(case.case_id, case)

        if not cases_by_id:
            raise RuntimeError("Unable to fetch Ghana court cases")

        cases = sorted(cases_by_id.values(), key=lambda case: case.date, reverse=True)
        logger.info("Fetched %s Ghana cases across both court collections", len(cases))
        return cases if had_fetch_error else set_cached(cache_key, cases)

    async def fetch_high_court_cases(self, country: str) -> List[CaseResult]:
        """Dedicated High Court query; it does not alter the Supreme Court query."""
        country_key = country.lower().strip()
        country_config = COUNTRY_CONFIG.get(country_key)
        if not country_config:
            raise ValueError(f"Unsupported country: {country}")

        cache_key = ("wikidata-high-cases", country_key)
        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        sparql_query = f"""
            SELECT DISTINCT ?item ?itemLabel ?itemDescription ?date ?legal_citation ?courtLabel ?sourceLabel ?commons_file
            (GROUP_CONCAT(DISTINCT CONCAT(STR(?judge_item), "|", ?judge); separator="||") AS ?judge_data)
            WHERE {{
                {{
                    SELECT DISTINCT ?item ?court WHERE {{
                        ?item (wdt:P31/(wdt:P279*)) wd:{country_config["high_court_case_class"]};
                              (wdt:P17/(wdt:P279*)) wd:{country_config["country_id"]};
                              wdt:P4884 wd:{country_config["high_court_id"]}.
                        BIND(wd:{country_config["high_court_id"]} AS ?court)
                    }}
                    LIMIT 1000
                }}
                OPTIONAL {{ ?item wdt:P577 ?date. }}
                OPTIONAL {{ ?item wdt:P1031 ?legal_citation. }}
                OPTIONAL {{ ?item wdt:P1433 ?source. }}
                OPTIONAL {{ ?item wdt:P996 ?commons_file. }}
                OPTIONAL {{
                    ?item wdt:P1594 ?judge_item.
                    ?judge_item rdfs:label ?judge.
                    FILTER(LANG(?judge) = "en")
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en". }}
            }}
            GROUP BY ?item ?itemLabel ?itemDescription ?date ?legal_citation ?courtLabel ?sourceLabel ?commons_file
            ORDER BY DESC(?date)
        """

        try:
            async def request():
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(
                        self.endpoint,
                        params={"query": sparql_query, "format": "json"},
                        headers=self.headers,
                    )
                    response.raise_for_status()
                    return response.json()

            data = await with_retries(request)
            cases = [
                case
                for binding in data.get("results", {}).get("bindings", [])
                if (case := self.parse_wikidata_binding(binding, country_key, "high")) is not None
            ]
            logger.info(f"Fetched {len(cases)} High Court cases from Wikidata for {country}")
            return set_cached(cache_key, cases)
        except Exception as e:
            logger.error(f"Error fetching High Court cases for {country}: {str(e)}")
            raise

    def parse_wikidata_binding(self, binding: Dict, country: str, court_level: str = "supreme") -> Optional[CaseResult]:
        try:
            case_id = binding.get("item", {}).get("value", "").split("/")[-1] or "unknown"
            
            # Extract and parse judges string
            judge_data = binding.get("judge_data", {}).get("value", "")
            judges_list = []
            if judge_data:
                judges_list = [
                    Judge(
                        name=parts[1].strip(),
                        wikidata_id=parts[0].rsplit("/", 1)[-1],
                    )
                    for entry in judge_data.split("||")
                    if (parts := entry.split("|", 1)) and len(parts) == 2 and parts[1].strip()
                ]
            
            # Safe date extraction
            raw_date = binding.get("date", {}).get("value")
            formatted_date = raw_date.split("T")[0] if raw_date else "Date not recorded"
            commons_file = binding.get("commons_file", {}).get("value")
            if commons_file and commons_file.startswith(("http://", "https://")):
                commons_file_url = commons_file
                file_name = unquote(urlparse(commons_file).path.rsplit("/", 1)[-1])
            elif commons_file:
                file_name = commons_file
                commons_file_url = f"https://commons.wikimedia.org/wiki/File:{quote(file_name)}"
            else:
                file_name = ""
                commons_file_url = None
            wikisource_index_url = (
                f"https://en.wikisource.org/wiki/Index:{quote(file_name)}"
                if court_level == "high" and file_name.lower().endswith(".pdf") else None
            )

            return CaseResult(
                case_id=case_id,
                title=binding.get("itemLabel", {}).get("value", "No title available"),
                description=binding.get("itemDescription", {}).get("value", "No description available"),
                date=formatted_date,
                citation=binding.get("legal_citation", {}).get("value", "Citation not available"),
                court=binding.get("courtLabel", {}).get("value", "Court not specified"),
                judges=judges_list if judges_list else [Judge(name="Judges unavailable")],
                article_url=binding.get("item", {}).get("value", ""),
                country=country.capitalize().replace("_", " "),
                court_level=court_level,
                wikisource_url=wikisource_index_url,
                commons_file_url=commons_file_url,
                source="Wikidata"
            )
        except Exception as e:
            logger.error(f"Error parsing binding: {str(e)}")
            return None

    async def fetch_translations(self, country: str, case_id: Optional[str] = None):
        cases = await self.fetch_cases(country)
        translations = []
        for case in cases:
            if case_id and case.case_id != case_id:
                continue

            translations.append({
                "case_id": case.case_id,
                "case_title": case.title,
                "available_languages": [
                    {
                        "language": "en",
                        "language_label": "English",
                        "wikidata_url": case.article_url,
                        "source": "Wikidata"
                    }
                ]
            })

        if case_id:
            return translations[0] if translations else None

        return translations
