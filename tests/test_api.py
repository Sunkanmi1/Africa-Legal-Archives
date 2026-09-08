from fastapi.testclient import TestClient
from main import app
from models import CaseResult, Judge
from services.wikidata_service import WikidataService
from services.wikisource_service import WikisourceService


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


