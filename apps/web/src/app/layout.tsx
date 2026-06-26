import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Engineering OS",
  description: "An AI-powered workspace that turns an idea into a production-grade repository.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-base font-sans text-text antialiased">{children}</body>
    </html>
  );
}
