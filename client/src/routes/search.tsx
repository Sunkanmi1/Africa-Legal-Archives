import { createFileRoute, Link, useSearch } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PageShell } from "@/components/site/PageShell";
import { SearchCase, SearchFilters, searchCases } from "@/lib/home.functions";

export const Route = createFileRoute("/search")({
  validateSearch: (search) => ({
    q: typeof search.q === "string" ? search.q : "",
  }),
  component: SearchPage,
  head: () => ({
    meta: [
      { title: "Search Ghana Court Cases" },
      { name: "description", content: "Search Ghana court cases by name, judge, court, year, and keywords." },
    ],
  }),
});

function SearchPage() {
  const { q: initialQuery } = useSearch({ from: "/search" });
  const [query, setQuery] = useState(initialQuery);
  const [year, setYear] = useState("");
  const [judge, setJudge] = useState("");
  const [court, setCourt] = useState("");
  const [results, setResults] = useState<SearchCase[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(Boolean(initialQuery));
  const [error, setError] = useState(false);

  async function loadResults(nextPage = 1) {
    setLoading(true);
    setError(false);
    const filters: SearchFilters = {
      q: query.trim(),
      page: nextPage,
      page_size: 20,
      judge: judge.trim() || undefined,
      court: court || undefined,
      year: year ? Number(year) : undefined,
    };
    try {
      const response = await searchCases({ data: filters });
      setResults(response.results);
      setTotal(response.total_results);
      setPage(response.page);
      setTotalPages(response.total_pages);
    } catch {
      setError(true);
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (initialQuery.trim()) void loadResults();
  }, []);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (query.trim() || year || judge.trim() || court) {
      void loadResults(1);
    } else {
      setResults([]);
      setTotal(0);
      setPage(1);
      setTotalPages(1);
      setError(false);
      setLoading(false);
    }
  }

  return (
    <PageShell withSidebar={false} searchPlaceholder="Search Ghana cases...">
      <div className="flex flex-col gap-8 px-5 py-10 lg:px-10">
        <header>
          <p className="eyebrow text-gold">Ghana Case Search</p>
          <h1 className="mt-2 text-3xl font-bold text-foreground">Find a Ghana court case</h1>
          <p className="mt-2 text-sm text-muted-foreground">Search by case name, judge, court, year, or keyword.</p>
        </header>

        <form onSubmit={submit} className="card-surface grid gap-4 p-5 md:grid-cols-[1fr_auto]">
          <label className="sr-only" htmlFor="case-search">Search cases</label>
          <input
            id="case-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try Tetteh v Hayford"
            className="h-11 rounded-md border border-input bg-surface px-3 text-sm text-foreground outline-none focus:border-gold focus:ring-1 focus:ring-gold"
          />
          <button type="submit" className="h-11 rounded-md bg-primary px-6 text-sm font-semibold text-primary-foreground hover:opacity-90">
            Search
          </button>
          <div className="grid gap-3 md:col-span-2 md:grid-cols-3">
            <label className="text-xs font-semibold text-muted-foreground">
              Year
              <input value={year} onChange={(event) => setYear(event.target.value)} inputMode="numeric" placeholder="Any year" className="mt-1 h-10 w-full rounded-md border border-input bg-surface px-3 text-sm font-normal text-foreground outline-none focus:border-gold" />
            </label>
            <label className="text-xs font-semibold text-muted-foreground">
              Judge
              <input value={judge} onChange={(event) => setJudge(event.target.value)} placeholder="Any judge" className="mt-1 h-10 w-full rounded-md border border-input bg-surface px-3 text-sm font-normal text-foreground outline-none focus:border-gold" />
            </label>
            <label className="text-xs font-semibold text-muted-foreground">
              Court
              <select value={court} onChange={(event) => setCourt(event.target.value)} className="mt-1 h-10 w-full rounded-md border border-input bg-surface px-3 text-sm font-normal text-foreground outline-none focus:border-gold">
                <option value="">Any court</option>
                <option value="Supreme Court">Supreme Court</option>
                <option value="High Court">High Court</option>
              </select>
            </label>
          </div>
        </form>

        <section aria-live="polite">
          <div className="flex items-end justify-between gap-4 border-b border-border pb-4">
            <div>
              <h2 className="text-xl font-bold text-foreground">Search results</h2>
              {!loading && !error ? <p className="mt-1 text-sm text-muted-foreground">{total.toLocaleString()} cases found</p> : null}
            </div>
            {totalPages > 1 ? <p className="text-sm text-muted-foreground">Page {page} of {totalPages}</p> : null}
          </div>

          {loading ? <p className="py-12 text-center text-sm text-muted-foreground">Loading cases...</p> : null}
          {error ? <p className="py-12 text-center text-sm text-destructive">We could not retrieve cases. Please try again.</p> : null}
          {!loading && !error && results.length === 0 ? <p className="py-12 text-center text-sm text-muted-foreground">Enter a case, year, judge, or court to search Ghana's case records.</p> : null}

          <div className="mt-5 grid gap-4">
            {results.map((result) => <ResultCard key={result.case_id} result={result} />)}
          </div>
          {totalPages > 1 ? (
            <div className="mt-6 flex justify-between gap-3">
              <button type="button" disabled={page === 1} onClick={() => void loadResults(page - 1)} className="rounded-md border border-border px-4 py-2 text-sm font-semibold text-foreground disabled:opacity-40">Previous</button>
              <button type="button" disabled={page === totalPages} onClick={() => void loadResults(page + 1)} className="rounded-md border border-border px-4 py-2 text-sm font-semibold text-foreground disabled:opacity-40">Next</button>
            </div>
          ) : null}
        </section>
      </div>
    </PageShell>
  );
}

function ResultCard({ result }: { result: SearchCase }) {
  return (
    <article className="card-surface p-5 transition-shadow hover:shadow-lg">
      <div className="flex flex-wrap items-center gap-3">
        <span className="eyebrow rounded bg-mint px-2 py-0.5 text-mint-foreground">Ghana</span>
        <span className="text-xs text-muted-foreground">{result.date}</span>
      </div>
      <h3 className="mt-3 text-lg font-bold text-foreground">{result.title}</h3>
      <p className="mt-1 text-sm text-muted-foreground">{result.citation} · {result.court}</p>
      <p className="mt-3 text-sm leading-relaxed text-foreground">{result.description}</p>
      <div className="mt-4 flex items-center justify-between gap-3">
        <span className="text-xs text-muted-foreground">{result.judges.map((judge) => judge.name).join(", ")}</span>
        <Link
          to="/cases/$caseId"
          params={{ caseId: result.case_id }}
          className="text-sm font-semibold text-gold hover:underline"
        >
          Read case
        </Link>
      </div>
    </article>
  );
}
