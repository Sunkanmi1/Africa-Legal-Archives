import { createServerFn } from "@tanstack/react-start";

export interface CaseOfTheDay {
  caseId: string;
  title: string;
  summary: string;
  image: string;
  imageAlt: string;
  caseUrl: string;
  metadata: { label: string; value: string }[];
}

export interface TrendingCase {
  caseId: string;
  country: string;
  year: string;
  title: string;
  blurb: string;
  court: string;
}

export interface MediaItem {
  title: string;
  src: string;
  caption: string;
  sourcePage?: string | undefined;
  license?: string | null | undefined;
}

export interface JudgeProfile {
  name: string;
  case_count: number;
  wikipedia_title?: string | null;
  wikipedia_url?: string | null;
  media: MediaItem[];
}

export interface HomeStats {
  archived_cases: number;
  nations_covered: number;
  last_update: string;
}

export interface SearchCase {
  case_id: string;
  title: string;
  description: string;
  date: string;
  citation: string;
  court: string;
  judges: { name: string }[];
  country?: string;
  court_level?: "supreme" | "high";
  case_type?: string;
}

export interface SearchResponse {
  results: SearchCase[];
  total_results: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SearchFilters {
  q?: string;
  page?: number;
  page_size?: number;
  year?: number;
  judge?: string;
  court?: string;
  citation?: string;
  court_level?: "supreme" | "high";
  case_type?: string;
  has_full_text?: boolean;
  data_complete?: boolean;
}

interface MediaResponse {
  items: {
    thumbnail_url: string;
    description: string;
    title: string;
    source_page?: string;
    license?: string | null;
  }[];
}

const commonsFallbackCategory = "Category:Supreme Court of Ghana building";

function caseImageIndex(caseId: string, imageCount: number) {
  const hash = Array.from(caseId).reduce((value, character) => value + character.charCodeAt(0), 0);
  return imageCount ? hash % imageCount : 0;
}

interface BackendCase {
  case_id: string;
  title: string;
  description: string;
  date: string;
  citation: string;
  court: string;
  judges: { name: string }[];
  article_url: string;
  country?: string;
  wikisource_url?: string | null;
  full_text?: string | null;
  opinion_summary?: string | null;
}

const fallbackCaseOfTheDay: CaseOfTheDay = {
  caseId: "",
  title: "Ghana case unavailable",
  summary: "The daily Ghana court case is temporarily unavailable.",
  image: "",
  imageAlt: "",
  caseUrl: "/search",
  metadata: [
    { label: "Jurisdiction", value: "Ghana" },
    { label: "Court", value: "Unavailable" },
    { label: "Decided", value: "Unavailable" },
    { label: "Judges", value: "Unavailable" },
    { label: "Wikidata QID", value: "Unavailable" },
  ],
};

const fallbackTrending: TrendingCase[] = [
  {
    country: "Ghana",
    year: "",
    title: "No trending cases available",
    blurb: "Ghana case data is temporarily unavailable.",
    court: "Ghana courts",
    caseId: "",
  },
];

async function fetchBackend<T>(path: string): Promise<T | null> {
  const baseUrl =
    process.env["BACKEND_API_URL"] ?? import.meta.env["VITE_API_BASE_URL"] ?? "/";
  if (!baseUrl) return null;
  try {
    const res = await fetch(`${baseUrl.replace(/\/$/, "")}${path}`, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(15000),
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export const getCaseOfTheDay = createServerFn({ method: "GET" }).handler(
  async (): Promise<CaseOfTheDay> => {
    const data = await fetchBackend<BackendCase>("/api/case-of-the-day?country=ghana");
    if (!data) return fallbackCaseOfTheDay;
    const matchingMedia = await fetchBackend<MediaResponse>(
      `/api/media?query=${encodeURIComponent(data.title)}&limit=10`,
    );
    const media = matchingMedia?.items.length
      ? matchingMedia
      : await fetchBackend<MediaResponse>(
          `/api/media?category=${encodeURIComponent(commonsFallbackCategory)}&limit=4`,
        );
    const image = media?.items[caseImageIndex(data.case_id, media?.items.length ?? 0)];
    return {
      caseId: data.case_id,
      title: data.title,
      summary: data.opinion_summary || data.description,
      image: image?.thumbnail_url ?? "",
      imageAlt: image?.description || data.title,
      caseUrl: `/cases/${encodeURIComponent(data.case_id)}`,
      metadata: [
        { label: "Jurisdiction", value: data.country || "Ghana" },
        { label: "Court", value: data.court },
        { label: "Decided", value: data.date },
        { label: "Judges", value: data.judges.map((judge) => judge.name).join(", ") },
        { label: "Wikidata QID", value: data.case_id },
      ],
    };
  },
);

export const getTrendingCases = createServerFn({ method: "GET" }).handler(
  async (): Promise<TrendingCase[]> => {
    const response = await fetchBackend<BackendCase[]>("/api/trending?country=ghana&limit=4");
    const cases = (response ?? []).map((item) => ({
      country: item.country ?? "Ghana",
      year: item.date.slice(0, 4),
      title: item.title,
      blurb: item.description,
      court: item.court,
      caseId: item.case_id,
    }));
    return cases.length > 0 ? cases : fallbackTrending;
  },
);

export const getMediaLibrary = createServerFn({ method: "GET" }).handler(
  async (): Promise<MediaItem[]> => {
    const data = await fetchBackend<MediaResponse>(
      "/api/media?category=Category%3ASupreme%20Court%20of%20Ghana%20building&limit=3",
    );
    const items = data?.items?.map((item) => ({
      title: item.title,
      src: item.thumbnail_url,
      caption: item.description || item.title,
      sourcePage: item.source_page,
      license: item.license,
    }));
    return items ?? [];
  },
);

export const getAllMedia = createServerFn({ method: "GET" }).handler(
  async (): Promise<MediaItem[]> => {
    const data = await fetchBackend<MediaResponse>(
      "/api/media?category=Category%3A1st%20GOIF-Effutu%20workshop%202023&limit=500",
    );
    const items = data?.items?.map((item) => ({
      title: item.title,
      src: item.thumbnail_url,
      caption: item.description || item.title,
      sourcePage: item.source_page,
      license: item.license,
    }));
    return items ?? [];
  },
);

export const getJudges = createServerFn({ method: "GET" }).handler(
  async (): Promise<JudgeProfile[]> => {
    const data = await fetchBackend<JudgeProfile[]>("/api/judges?limit=100");
    return data ?? [];
  },
);

export const getHomeStats = createServerFn({ method: "GET" }).handler(
  async (): Promise<HomeStats> => {
    const data = await fetchBackend<HomeStats>("/api/stats");
    return data ?? { archived_cases: 0, nations_covered: 1, last_update: "Unavailable" };
  },
);

export const searchCases = createServerFn({ method: "GET" })
  .validator((filters: SearchFilters) => filters)
  .handler(async ({ data }): Promise<SearchResponse> => {
    const params = new URLSearchParams({ country: "ghana" });
    for (const [key, value] of Object.entries(data)) {
      if (value !== undefined && value !== "") params.set(key, String(value));
    }
    const response = await fetchBackend<SearchResponse>(`/api/search?${params.toString()}`);
    return (
      response ?? {
        results: [],
        total_results: 0,
        page: data.page ?? 1,
        page_size: data.page_size ?? 20,
        total_pages: 1,
      }
    );
  });
