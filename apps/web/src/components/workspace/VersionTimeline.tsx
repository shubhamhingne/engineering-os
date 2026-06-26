import type { VersionSummary } from "@/lib/api";
import { cn } from "@/lib/cn";

// Version history visual (newest first, from the API). Pure.
export function VersionTimeline({ versions }: { versions: VersionSummary[] }) {
  if (!versions.length) return <p className="text-sm text-text-muted">No versions yet.</p>;
  return (
    <div className="flex items-center">
      {versions.map((v, i) => (
        <div key={v.version} className="flex items-center">
          {i > 0 && <div className="h-0.5 w-12 bg-line" />}
          <div className="flex min-w-[72px] flex-col items-center gap-1.5">
            <span className={cn("h-3 w-3 rounded-full border-2 border-base", v.source === "ai" ? "bg-accent" : "bg-action")} />
            <span className="text-center text-[11px] leading-tight">
              <b className="font-mono font-medium">v{v.version}</b>
              <br />
              <span className="text-text-muted">{v.source}</span>
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
