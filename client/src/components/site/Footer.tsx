export function Footer() {
  return (
    <footer className="border-t border-border bg-primary text-primary-foreground">
      <div className="mx-auto grid max-w-[1280px] gap-10 px-5 py-12 md:grid-cols-[2fr_1fr_1fr]">
        <div>
          <div className="flex items-center gap-2">
            <span
              aria-hidden
              className="grid size-8 place-items-center rounded-md bg-gold-soft font-serif text-sm font-bold text-primary"
            >
              W
            </span>
            <span className="font-serif text-lg font-bold">WikiLegal Africa</span>
          </div>
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-primary-foreground/70">
            A collaborative platform for the preservation and accessibility of African legal knowledge. Operated as a
            community-driven repository under Creative Commons.
          </p>
          <p className="mt-4 text-xs text-primary-foreground/50">
            © 2024 WikiLegal Africa. Knowledge is the foundation of justice.
          </p>
        </div>

        <div>
          <p className="eyebrow text-gold-soft">Ecosystem</p>
          <ul className="mt-4 space-y-2 text-sm text-primary-foreground/70">
            <li>Wikidata</li>
            <li>Wikimedia Commons</li>
            <li>WikiSource</li>
          </ul>
        </div>

        <div>
          <p className="eyebrow text-gold-soft">Legal</p>
          <ul className="mt-4 space-y-2 text-sm text-primary-foreground/70">
            <li>Legal Disclaimer</li>
            <li>Privacy Policy</li>
            <li>Submit Case Record</li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
