import asyncio
from fastapi.testclient import TestClient
from main import app
from models import CaseResult, Judge
from services.wikidata_service import WikidataService
from services.wikisource_service import WikisourceService
from services.popularity import case_popularity
from routes import trending


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_countries():
    response = client.get("/api/countries")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["total_countries"] == 1
    assert response.json()["countries"][0]["code"] == "ghana"


def test_search_pagination_and_filters(monkeypatch):
    cases = [CaseResult(
        case_id="Q1",
        title="Ghana Case",
        description="A test case",
        date="2024-01-01",
        citation="GH-1",
        court="Supreme Court of Ghana",
        judges=[Judge(name="Ama Mensah")],
        article_url="https://www.wikidata.org/wiki/Q1",
        country="Ghana",
    )]

    async def fake_fetch_cases(self, country):
        return cases

    async def fake_enrich(self, cases):
        return cases

    monkeypatch.setattr(WikidataService, "fetch_cases", fake_fetch_cases)
    monkeypatch.setattr(WikisourceService, "enrich_case", fake_enrich)
    response = client.get("/api/search?country=ghana&year=2024&page=1&page_size=1")

    assert response.status_code == 200
    assert response.json()["total_results"] == 1
    assert response.json()["total_pages"] == 1
    assert response.json()["results"][0]["case_id"] == "Q1"


def test_search_filters_by_court_level(monkeypatch):
    cases = [
        CaseResult(
            case_id="Q1", title="Supreme Case", description="Supreme Court test case",
            date="2024-01-01", citation="SC-1", court="Supreme Court of Ghana",
            judges=[Judge(name="Ama Mensah")], article_url="https://www.wikidata.org/wiki/Q1",
            country="Ghana", court_level="supreme",
        ),
        CaseResult(
            case_id="Q2", title="High Case", description="High Court test case",
            date="1959-09-29", citation="HC-1", court="High Court of Ghana",
            judges=[Judge(name="N. A. Ollennu")], article_url="https://www.wikidata.org/wiki/Q2",
            country="Ghana", court_level="high",
            wikisource_url="https://en.wikisource.org/wiki/Index:Example.pdf",
            commons_file_url="https://commons.wikimedia.org/wiki/File:Example.pdf",
        ),
    ]

    async def fake_fetch_cases(self, country):
        return cases

    monkeypatch.setattr(WikidataService, "fetch_cases", fake_fetch_cases)
    response = client.get("/api/search?country=ghana&court_level=high")

    assert response.status_code == 200
    assert response.json()["total_results"] == 1
    result = response.json()["results"][0]
    assert result["case_id"] == "Q2"
    assert result["court_level"] == "high"
    assert result["wikisource_url"].endswith("Example.pdf")


def test_wikisource_query_ignores_placeholder_citation(monkeypatch):
    observed = {}

    async def fake_search(self, query: str):
        observed["query"] = query
        return None

    monkeypatch.setattr(WikisourceService, "_search_wikisource", fake_search)

    case = CaseResult(
        case_id="Q123",
        title="Cleland Van Lare vs J.A Anthony",
        description="High Court case",
        date="1959-09-29",
        citation="Citation not available",
        court="High Court of Ghana",
        judges=[Judge(name="Justice A")],
        article_url="https://www.wikidata.org/wiki/Q123",
        country="Ghana",
        court_level="high",
    )

    asyncio.run(WikisourceService()._fetch_case_details(case))

    assert observed["query"] == "Cleland Van Lare vs J.A Anthony"


def test_trending_uses_popularity_and_full_collection(monkeypatch):
    cases = [
        CaseResult(
            case_id="Q1", title="Supreme Case", description="Supreme", date="2024-01-01",
            citation="SC-1", court="Supreme Court of Ghana", judges=[Judge(name="Judge 1")],
            article_url="https://www.wikidata.org/wiki/Q1", country="Ghana", court_level="supreme",
        ),
        CaseResult(
            case_id="Q2", title="High Case", description="High", date="1959-01-01",
            citation="HC-1", court="High Court of Ghana", judges=[Judge(name="Judge 2")],
            article_url="https://www.wikidata.org/wiki/Q2", country="Ghana", court_level="high",
        ),
    ]

    async def fake_fetch_cases(self, country):
        return cases

    monkeypatch.setattr(trending.WikidataService, "fetch_cases", fake_fetch_cases)
    case_popularity._counts.clear()

    fallback = client.get("/api/trending?country=ghana&limit=2")
    assert fallback.status_code == 200
    assert {item["case_id"] for item in fallback.json()} == {"Q1", "Q2"}

    case_popularity.record([cases[1]])
    ranked = client.get("/api/trending?country=ghana&limit=1")
    assert ranked.status_code == 200
    assert ranked.json()[0]["case_id"] == "Q2"


