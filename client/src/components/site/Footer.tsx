import africaLegalArchiveLogo from "@/assets/panla.png";
import Goif_Logo from "@/assets/Goif Logo.png";
import { Link } from "@tanstack/react-router";

export function Footer() {
  return (
    <footer className="border-t border-border bg-primary text-primary-foreground">
      <div className="mx-auto grid max-w-[1280px] gap-1 px-5 py-10 sm:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_1fr] lg:items-start">
        <div>
          <div className="flex items-center gap-2">
            <img
              src={africaLegalArchiveLogo}
              alt="Africa Legal Archive logo"
              className="size-10 rounded-full object-cover"
            />
            <span className="font-serif text-lg font-bold">PALA</span>
          </div>

          <p className="mt-4 max-w-sm text-sm leading-relaxed text-primary-foreground/70">
            A collaborative platform for the preservation and accessibility of African legal knowledge.
            Operated as a community-driven repository under Creative Commons.
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
            <li>CC by 4.0</li>
          </ul>
        </div>

        <div>
          <Link to="https://globalopeninitiative.org/">
           <img
              src={Goif_Logo}
              alt="GLOBAL OPEN INITIATIVE FOUNDATION logo"
              className="h-15 w-30"
            />
          <p className="eyebrow text-sm text-primary-foreground/70">project by GLOBAL OPEN INNITIATIVE FOUNDATION</p>
          </Link>
        </div>
      </div>
    </footer>
  );
}
