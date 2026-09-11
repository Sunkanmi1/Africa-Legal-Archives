import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PageShell } from "@/components/site/PageShell";
import { getJudges, JudgeProfile } from "@/lib/home.functions";

export const Route = createFileRoute("/judges")({
  component: JudgesPage,
  head: () => ({
    meta: [
      { title: "Judges | Ghana Supreme Court Legal Archive" },
      {
        name: "description",
        content:
          "Explore Ghana Supreme Court judges, their cases, Wikipedia articles, and related Commons media.",
      },
    ],
  }),
});

function JudgesPage() {
  const [judges, setJudges] = useState<JudgeProfile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getJudges()])
      .then(([profiles]) => {
        setJudges(profiles);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageShell withSidebar={false} searchPlaceholder="Search Ghana cases...">
      <div className="flex flex-col gap-8 px-5 py-10 lg:px-10">
        <header>
          <p className="eyebrow text-gold">Ghana Supreme Court</p>
          <h1 className="mt-2 text-3xl font-bold text-foreground">Judges and Legal Voices</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            Explore judges connected to Ghanaian cases, with links to available Wikipedia articles
            and related Commons media.
          </p>
        </header>

        {loading ? (
          <p className="py-12 text-center text-sm text-muted-foreground">
            Loading judge profiles...
          </p>
        ) : null}
        {!loading && judges.length === 0 ? (
          <p className="rounded-lg border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
            No judge profiles are currently available.
          </p>
        ) : null}
        <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {judges.map((judge) => {
            const content = (
              <>
                {judge.media[0] ? (
                  <img
                    src={judge.media[0].src}
                    alt={judge.media[0].caption || judge.name}
                    loading="lazy"
                    className="h-44 w-full object-cover"
                  />
                ) : null}
                <div className="p-5">
                  <p className="eyebrow text-gold">Judge</p>
                  <h2 className="mt-2 text-lg font-bold text-foreground">{judge.name}</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {judge.case_count.toLocaleString()} cases indexed
                  </p>
                  <p className="mt-4 text-sm font-semibold text-gold">View on Wikipedia</p>
                  {judge.media[0]?.license ? (
                    <p className="mt-3 text-xs text-muted-foreground">
                      Image license: {judge.media[0].license}
                    </p>
                  ) : null}
                </div>
              </>
            );

            return judge.wikipedia_url ? (
              <a
                key={judge.name}
                href={judge.wikipedia_url}
                target="_blank"
                rel="noreferrer"
                className="card-surface block overflow-hidden transition-shadow hover:shadow-lg"
              >
                {content}
              </a>
            ) : (
              <article key={judge.name} className="card-surface overflow-hidden">
                {content}
              </article>
            );
          })}
        </section>
      </div>
    </PageShell>
  );
}
