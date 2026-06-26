import type { VersionSummary } from "@/lib/api";
import { cn } from "@/lib/cn";
import { VersionTimeline } from "./VersionTimeline";

// Bottom zone: version timeline + activity feed.
export function BottomActivityPanel({ versions }: { versions: VersionSummary[] }) {
  return (
    <div className="grid grid-cols-[1.4fr_1fr] gap-6 overflow-hidden border-t border-border px-5 py-3">
      <div>
        <div className="mb-2.5 text-[11px] font-semibold uppercase tracking-wide text-text-muted">Version history</div>
        <VersionTimeline versions={versions} />
      </div>
      <div>
        <div className="mb-2.5 text-[11px] font-semibold uppercase tracking-wide text-text-muted">Activity</div>
        <ul className="space-y-1 text-[12.5px] text-text-secondary">
          {versions.slice(0, 3).map((v) => (
            <li key={v.version} className="flex items-center gap-2">
              <span className={cn("h-1.5 w-1.5 rounded-full", v.source === "ai" ? "bg-accent" : "bg-action")} />
              {v.source === "ai" ? "Generated" : "Edited"} · v{v.version}
            </li>
          ))}
          {!versions.length && <li className="text-text-muted">No activity yet.</li>}
        </ul>
      </div>
    </div>
  );
}
