import { createFileRoute, Link } from "@tanstack/react-router";
import { queryOptions, useSuspenseQuery } from "@tanstack/react-query";
import { PageShell } from "@/components/site/PageShell";
import { getCaseOfTheDay, getHomeStats, getTrendingCases } from "@/lib/home.functions";

const caseOfTheDayQuery = queryOptions({
  queryKey: ["case-of-the-day"],
  queryFn: () => getCaseOfTheDay(),
  staleTime: 10 * 60 * 1000,
  refetchInterval: 10 * 60 * 1000,
});

const trendingCasesQuery = queryOptions({
  queryKey: ["trending-cases"],
  queryFn: () => getTrendingCases(),
  staleTime: 5 * 60 * 1000,
});

const homeStatsQuery = queryOptions({
  queryKey: ["home-stats"],
  queryFn: () => getHomeStats(),
  staleTime: 5 * 60 * 1000,
});

function formatLastUpdate(value: string) {
  if (value === "Unavailable") return value;
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
}

export const Route = createFileRoute("/")({
  loader: ({ context }) =>
    Promise.all([
      context.queryClient.ensureQueryData(caseOfTheDayQuery),
      context.queryClient.ensureQueryData(trendingCasesQuery),
      context.queryClient.ensureQueryData(homeStatsQuery),
    ]),
  head: () => ({
    meta: [
      { title: "WikiLegal Africa — African Case Law & Legal Archive" },
      {
        name: "description",
        content:
          "Browse archived Ghanaian judgments, statutes and court records, freely accessible.",
      },
      { property: "og:title", content: "WikiLegal Africa — African Case Law & Legal Archive" },
      {
        property: "og:description",
        content: "Landmark judgments, statutes and court records from Ghana, freely accessible.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  const { data: caseOfTheDay } = useSuspenseQuery(caseOfTheDayQuery);
  const { data: trending } = useSuspenseQuery(trendingCasesQuery);
  const { data: homeStats } = useSuspenseQuery(homeStatsQuery);
  const stats = [
    { label: "Archived Cases", value: homeStats.archived_cases.toLocaleString() },
    { label: "Nations Covered", value: homeStats.nations_covered.toLocaleString() },
    { label: "Last Update", value: formatLastUpdate(homeStats.last_update) },
  ];

  return (
    <PageShell withSidebar={false}>
      <div className="flex flex-col gap-14 px-5 py-10 lg:px-10">
        {/* Case of the day */}
        <section className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
          <article className="relative overflow-hidden rounded-xl bg-primary text-primary-foreground shadow-[var(--shadow-hero)]">
            {caseOfTheDay.image ? (
              <img
                src={caseOfTheDay.image}
                alt={caseOfTheDay.imageAlt}
                width={1280}
                height={720}
                className="absolute inset-0 size-full object-cover opacity-25"
              />
            ) : null}
            <div className="relative flex flex-col gap-5 p-8 lg:p-10">
              <span className="eyebrow w-fit rounded-md bg-gold-soft px-3 py-1 text-primary">
                Case of the Day
              </span>
              <h1 className="max-w-xl text-3xl font-bold leading-tight lg:text-[2.75rem]">
                {caseOfTheDay.title}
              </h1>
              <p className="max-w-2xl text-sm leading-relaxed text-primary-foreground/80 lg:text-base">
                {caseOfTheDay.summary}
              </p>
              <div className="mt-2 flex flex-wrap gap-3">
                <a
                  href={caseOfTheDay.caseUrl}
                  className="rounded-md bg-gold-soft px-5 py-2.5 text-sm font-semibold text-primary transition-opacity hover:opacity-90"
                >
                  Read Full Judgment
                </a>
              </div>
            </div>
          </article>

          <aside className="card-surface p-6">
            <p className="eyebrow text-gold">Case Metadata</p>
            <dl className="mt-4 divide-y divide-border">
              {caseOfTheDay.metadata.map((m) => (
                <div key={m.label} className="flex items-center justify-between gap-4 py-3">
                  <dt className="text-sm text-muted-foreground">{m.label}</dt>
                  <dd className="text-right text-sm font-semibold text-foreground">{m.value}</dd>
                </div>
              ))}
            </dl>
          </aside>
        </section>

        {/* Stats */}
        <section className="grid gap-5 sm:grid-cols-3">
          {stats.map((s) => (
            <div key={s.label} className="card-surface p-6">
              <p className="eyebrow text-muted-foreground">{s.label}</p>
              <p className="mt-2 font-serif text-3xl font-bold text-foreground">{s.value}</p>
            </div>
          ))}
        </section>

        {/* Trending */}
        <section>
          <div className="flex items-end justify-between gap-4">
            <h2 className="text-2xl font-bold text-foreground">Trending Cases</h2>
            <Link
              to="/search"
              search={{ q: "" }}
              className="text-sm font-semibold text-gold hover:underline"
            >
              Browse All →
            </Link>
          </div>
          <div className="mt-5 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
            {trending.map((c) => (
              <Link
                key={c.caseId || c.title}
                to={`/cases/${encodeURIComponent(c.caseId || "")}`}
                search={{ q: c.caseId ? c.title : "" }}
                className="card-surface flex flex-col gap-3 p-5 transition-shadow hover:shadow-lg"
              >
                <div className="flex items-center gap-2">
                  <span className="eyebrow rounded bg-mint px-2 py-0.5 text-mint-foreground">
                    {c.country}
                  </span>
                  <span className="text-xs text-muted-foreground">{c.year}</span>
                </div>
                <h3 className="text-base font-bold leading-snug text-foreground">{c.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">{c.blurb}</p>
                <p className="mt-auto pt-3 text-xs font-semibold text-gold">{c.court}</p>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </PageShell>
  );
}
