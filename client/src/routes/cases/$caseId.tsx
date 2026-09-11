import { createFileRoute } from "@tanstack/react-router";
import { queryOptions, useSuspenseQuery } from "@tanstack/react-query";
import { PageShell } from "@/components/site/PageShell";
import { getCaseById } from "@/lib/case.functions";

const caseDetailQuery = (caseId: string) =>
  queryOptions({
    queryKey: ["case", caseId],
    queryFn: () => getCaseById({ data: { caseId } }),
    staleTime: 5 * 60 * 1000,
  });

export const Route = createFileRoute("/cases/$caseId")({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(caseDetailQuery(params.caseId)),
  head: () => ({
    meta: [
      { title: "Ghana Supreme Court Case — Case Record" },
      {
        name: "description",
        content: "Read a Ghana Supreme Court case record and its available metadata.",
      },
    ],
  }),
  component: CaseView,
});

function CaseView() {
  const { caseId } = Route.useParams();
  const { data: caseDetail } = useSuspenseQuery(caseDetailQuery(caseId));

  return (
    <PageShell withSidebar={false} searchPlaceholder="Search precedents...">
      <div className="flex flex-col gap-10 px-5 py-10 lg:px-10">
        <header className="flex flex-col gap-4 border-b border-border pb-8">
          <div className="flex flex-wrap items-center gap-3">
            <span className="eyebrow rounded bg-gold-soft px-3 py-1 text-primary">
              {caseDetail.badge}
            </span>
            <span className="text-xs font-semibold text-muted-foreground">
              {caseDetail.citation}
            </span>
          </div>
          <h1 className="max-w-3xl text-3xl font-bold leading-tight text-foreground lg:text-[2.5rem]">
            {caseDetail.title}
          </h1>
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <span>{caseDetail.date}</span>
            <span>{caseDetail.court}</span>
            <span>{caseDetail.bench}</span>
            <span>
              {caseDetail.commonsFileUrl ? (
                <a
                  href={caseDetail.commonsFileUrl}
                  download
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-md bg-primary text-center p-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
                >
                  Download PDF
                </a>
              ) : null}{" "}
            </span>
          </div>
        </header>

        <div className="grid gap-10 lg:grid-cols-[1.7fr_1fr]">
          <article className="flex flex-col gap-5">
            <h2 className="text-xl font-bold text-foreground">Case overview</h2>
            <p className="text-[15px] leading-8 text-foreground">{caseDetail.description}</p>

            {caseDetail.fullText ? (
              <>
                <h2 className="mt-4 text-xl font-bold text-foreground">JUDGEMENT</h2>
                <div className="whitespace-pre-wrap text-[15px] leading-8 text-foreground">
                  {caseDetail.fullText}
                </div>
              </>
            ) : (
              <p className="rounded-md bg-secondary p-5 text-sm leading-relaxed text-muted-foreground">
                The full judgment text is not yet available for this case. The record above is
                sourced from Wikidata.
              </p>
            )}
          </article>

          <aside className="flex flex-col gap-6">
            <div className="card-surface p-6">
              <p className="eyebrow text-gold">Case summary</p>
              <dl className="mt-4 divide-y divide-border">
                {caseDetail.summary.map((item) => (
                  <div key={item.label} className="py-3">
                    <dt className="text-xs text-muted-foreground">{item.label}</dt>
                    <dd className="mt-1 text-sm font-semibold leading-relaxed text-foreground">
                      {item.value}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>

            <div className="flex flex-col gap-3">
              {caseDetail.commonsPreviewUrl ? (
                <div className="overflow-hidden rounded-md border border-border bg-secondary">
                  <img
                    src={caseDetail.commonsPreviewUrl}
                    alt="First page of the judgment scan from Wikimedia Commons"
                    className="h-auto w-full"
                  />
                </div>
              ) : null}
              {caseDetail.wikisourceUrl ? (
                <a
                  href={caseDetail.wikisourceUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-md bg-primary px-5 py-3 text-center text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
                >
                  Read on Wikisource
                </a>
              ) : null}
              {caseDetail.commonsFileUrl ? (
                <a
                  href={caseDetail.commonsFileUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-md border border-border px-5 py-3 text-center text-sm font-semibold text-foreground transition-colors hover:bg-accent"
                >
                  View judgment scan on Commons
                </a>
              ) : null}
              <a
                href={caseDetail.articleUrl}
                target="_blank"
                rel="noreferrer"
                className="rounded-md border border-border px-5 py-3 text-center text-sm font-semibold text-foreground transition-colors hover:bg-accent"
              >
                View Wikidata record
              </a>
            </div>
          </aside>
        </div>
      </div>
    </PageShell>
  );
}
