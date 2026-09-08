import type { ReactNode } from "react";
import { Footer } from "./Footer";
import { Sidebar } from "./Sidebar";
import { TopNav } from "./TopNav";

export function PageShell({
  children,
  withSidebar = true,
  searchPlaceholder,
}: {
  children: ReactNode;
  withSidebar?: boolean;
  searchPlaceholder?: string;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <TopNav searchPlaceholder={searchPlaceholder} />
      <div className="mx-auto flex w-full max-w-[1280px] flex-1 items-stretch">
        {withSidebar ? <Sidebar /> : null}
        <main className="min-w-0 flex-1">{children}</main>
      </div>
      <Footer />
    </div>
  );
}
