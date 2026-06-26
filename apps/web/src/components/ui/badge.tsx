import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

export function Badge({
  children,
  tone = "neutral",
  className,
}: {
  children: ReactNode;
  tone?: "neutral" | "ai" | "success";
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 font-mono text-[11px]",
        tone === "ai" && "border-accent/40 text-accent",
        tone === "success" && "border-success/40 text-success",
        tone === "neutral" && "border-line text-text-secondary",
        className,
      )}
    >
      {children}
    </span>
  );
}
