"use client";
import type { ArtifactType } from "@/lib/api";
import { cn } from "@/lib/cn";

const ITEMS: { type: string; label: string; enabled: boolean }[] = [
  { type: "vision", label: "Vision", enabled: true },
  { type: "prd", label: "PRD", enabled: true },
  { type: "readme", label: "README", enabled: true },
  { type: "adr", label: "ADR", enabled: true },
];

// Data-driven typed artifact tree. Adding a type is a config line — scales to 20 (ADR-0004).
export function ArtifactTree({
  active,
  present,
  onSelect,
}: {
  active: string;
  present: string[];
  onSelect: (t: ArtifactType) => void;
}) {
  return (
    <nav className="p-2.5">
      <div className="px-2 py-1.5 text-[11px] uppercase tracking-wide text-text-muted">Artifacts</div>
      {ITEMS.map((it) => {
        const isActive = active === it.type;
        const has = present.includes(it.type);
        return (
          <button
            key={it.type}
            disabled={!it.enabled}
            onClick={() => onSelect(it.type as ArtifactType)}
            className={cn(
              "flex w-full items-center gap-2.5 rounded-md px-2 py-1.5 text-left text-[13px]",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:opacity-40",
              isActive ? "bg-raised text-text" : "text-text-secondary hover:bg-raised/60",
            )}
          >
            <span
              className={cn(
                "h-1.5 w-1.5 rounded-full",
                has ? (it.type === "vision" ? "bg-accent" : "bg-success") : "bg-text-muted",
              )}
            />
            {it.label}
          </button>
        );
      })}
    </nav>
  );
}
