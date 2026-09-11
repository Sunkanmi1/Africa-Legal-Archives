from pydantic import BaseModel, Field
from typing import Optional, List

class Judge(BaseModel):
    name: str
    role: Optional[str] = None
    wikidata_id: Optional[str] = None


class CaseResult(BaseModel):
    case_id: str
    title: str
    description: str
    date: str
    citation: str
    court: str
    judges: List[Judge]
    article_url: str
    country: Optional[str] = None
    court_level: str = "supreme"
    case_type: str = "general"
    # Wikisource Integration
    wikisource_url: Optional[str] = None
    commons_file_url: Optional[str] = None
    commons_preview_url: Optional[str] = None
    full_text: Optional[str] = None
    opinion_summary: Optional[str] = None
    source: str = "Wikidata"

class Country(BaseModel):
    code: str
    name: str
    wikidata_id: str

class SearchResponse(BaseModel):
    success: bool
    results: List[CaseResult]
    total_results: int
    page: int = 1
    page_size: int = 50
    total_pages: int = 1

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    environment: str
    version: str

class CountriesResponse(BaseModel):
    success: bool
    total_countries: int
    countries: List[Country]

class TranslationLanguage(BaseModel):
    language_code: str
    language_label: str
    wikidata_url: str
    source: str


class TranslationResult(BaseModel):
    case_id: str
    case_title: str
    available_language: List[TranslationLanguage]

class TranslationResponse(BaseModel):
    success: bool
    total_cases:int
    results: List[TranslationResult]

class StatResponse(BaseModel):
    success: bool
    archived_cases: int
    nations_covered: int
    last_update: str

class MediaItem(BaseModel):
    title: str
    thumbnail_url: str
    full_url: str
    description: str
    source_page: str
    license: Optional[str] = None
    media_type: str = "image"
    category: Optional[str] = None

class MediaResponse(BaseModel):
    success: bool
    items: List[MediaItem]

class JudgeProfile(BaseModel):
    name: str
    case_count: int
    wikipedia_title: Optional[str] = None
    wikipedia_url: Optional[str] = None
    media: List[MediaItem] = Field(default_factory=list)

class QualityResponse(BaseModel):
    success: bool
    total_cases: int
    duplicate_case_ids: List[str]
    missing_dates: int
    missing_citations: int
    missing_judges: int
    invalid_qids: int
