import { Link } from "@tanstack/react-router";
import { FormEvent, useState } from "react";
import africaLegalArchiveLogo from "@/assets/panla.png";

const links = [
  { label: "Home", to: "/" },
  { label: "Browse", to: "/search" },
  { label: "Judges", to: "/judges" },
] as const;

export function TopNav({ searchPlaceholder = "Search statutes..." }: { searchPlaceholder?: string | undefined }) {
  const [query, setQuery] = useState("");

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = query.trim();
    if (value) window.location.assign(`/search?q=${encodeURIComponent(value)}`);
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-primary text-primary-foreground">
      <div className="mx-auto flex h-[71px] max-w-[1280px] items-center gap-6 px-5">
        <Link to="/" className="flex shrink-0 items-center gap-2">
          <img
            src={africaLegalArchiveLogo}
            alt="Africa Legal Archive logo"
            className="size-10 rounded-full object-cover"
          />
          <span className="font-serif text-lg font-bold tracking-tight">PALA</span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          {links.map((l) => (
            <Link
              key={l.label}
              to={l.to}
              className="text-sm text-primary-foreground/75 transition-colors hover:text-gold-soft [&.active]:text-gold-soft"
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <form onSubmit={submitSearch} className="relative min-w-0 flex-1 sm:flex-none">
            <span className="sr-only">Search</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-label="Search Ghana Supreme Court cases"
              placeholder={searchPlaceholder}
              className="h-9 w-full rounded-md border border-primary-foreground/20 bg-primary-foreground/10 pl-9 pr-3 text-sm text-primary-foreground placeholder:text-primary-foreground/50 focus:border-gold-soft focus:outline-none sm:w-56 lg:w-72"
            />
            <svg
              aria-hidden
              viewBox="0 0 24 24"
              className="pointer-events-none absolute left-2.5 top-2.5 size-4 text-primary-foreground/50"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
          </form>
        </div>
      </div>
    </header>
  );
}
