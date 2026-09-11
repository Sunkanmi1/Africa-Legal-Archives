import { Link } from "@tanstack/react-router";

const categories = [
  {
    label: "Home",
    to: "/" as const,
    icon: "M3 11 12 4l9 7v8a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z",
  },
  {
    label: "Judges",
    to: "/judges" as const,
    icon: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8m-7 9a7 7 0 0 1 14 0",
  },
];

export function Sidebar() {
  return (
    <aside className="hidden w-[248px] shrink-0 self-stretch border-r border-border bg-surface lg:block">
      <div className="sticky top-[71px] flex flex-col gap-6 p-6">
        <div>
          <p className="eyebrow text-gold">Browse Laws</p>
          <p className="mt-1 text-xs text-muted-foreground">Ghana Jurisdiction</p>
        </div>

        <nav className="flex flex-col gap-1">
          {categories.map((c) => (
            <Link
              key={c.label}
              to={c.to}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground [&.active]:bg-accent [&.active]:font-semibold [&.active]:text-foreground"
            >
              <svg
                aria-hidden
                viewBox="0 0 24 24"
                className="size-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
              >
                <path d={c.icon} />
              </svg>
              {c.label}
            </Link>
          ))}
        </nav>

        <Link to="/search" className="text-xs font-semibold text-gold hover:underline">
          Browse Case Records →
        </Link>

        <div className="mt-auto flex flex-col gap-1 border-t border-border pt-5 text-sm text-muted-foreground">
          <span className="cursor-default rounded-md px-3 py-2 hover:bg-accent">Settings</span>
          <span className="cursor-default rounded-md px-3 py-2 hover:bg-accent">Help</span>
        </div>
      </div>
    </aside>
  );
}
