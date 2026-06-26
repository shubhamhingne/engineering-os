import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Engineering OS",
  description: "An AI-powered workspace that turns an idea into a production-grade repository.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="flex h-12 items-center border-b border-border px-6">
          <span className="font-semibold">Engineering OS</span>
          <span className="ml-3 text-sm text-text-secondary">Idea → repository</span>
        </header>
        <main className="mx-auto max-w-3xl p-6">{children}</main>
      </body>
    </html>
  );
}
