"use client";
import { useEffect, useState } from "react";
import { Check, Download, Loader2, X } from "lucide-react";
import { api, exportDownloadUrl, streamExport, type ExportDone, type ExportJob } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

const PHASES = ["queued", "preparing", "generating", "packaging", "verifying"];
const PHASE_LABEL: Record<string, string> = {
  queued: "Queued",
  preparing: "Validating artifacts",
  generating: "Building README",
  packaging: "Packaging ZIP",
  verifying: "Verifying",
};

// Export deserves a dedicated experience, not a modal. Replaces the right zone (ADR-0006).
export function ExportPanel({ projectId, onClose }: { projectId: string; onClose: () => void }) {
  const [phase, setPhase] = useState<string | null>(null);
  const [done, setDone] = useState<ExportDone | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [history, setHistory] = useState<ExportJob[]>([]);

  async function loadHistory() {
    try {
      setHistory(await api.listExports(projectId));
    } catch {
      /* none */
    }
  }
  useEffect(() => {
    void loadHistory();
  }, [projectId]);

  async function run() {
    setRunning(true);
    setError(null);
    setDone(null);
    setPhase("queued");
    try {
      await streamExport(projectId, {
        onPhase: (p) => setPhase(p),
        onDone: async (d) => {
          setDone(d);
          await loadHistory();
        },
        onError: (d) => setError(d),
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning(false);
      setPhase(null);
    }
  }

  const currentIdx = phase ? PHASES.indexOf(phase) : done ? PHASES.length : -1;

  return (
    <div className="flex h-full flex-col gap-3.5 overflow-auto border-l border-border p-3.5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Export</h2>
        <button onClick={onClose} aria-label="Close export" className="text-text-muted hover:text-text">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="rounded-lg border border-line bg-raised p-3">
        {PHASES.map((p, i) => {
          const complete = i < currentIdx || (!!done && currentIdx === PHASES.length);
          const active = running && i === currentIdx;
          return (
            <div
              key={p}
              className={cn("flex items-center gap-2.5 py-1 text-[13px]", complete || active ? "text-text" : "text-text-muted")}
            >
              <span
                className={cn(
                  "grid h-4 w-4 place-items-center rounded-full",
                  active ? "bg-accent/20 text-accent-soft" : complete ? "bg-success/15 text-success" : "bg-sunken text-text-muted",
                )}
              >
                {active ? <Loader2 className="h-2.5 w-2.5 animate-spin" /> : <Check className="h-2.5 w-2.5" />}
              </span>
              {PHASE_LABEL[p]}
            </div>
          );
        })}
      </div>

      {error && <p className="text-[13px] text-danger">{error}</p>}

      {done ? (
        <div className="rounded-lg border border-line bg-raised p-3">
          <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-text-muted">Download center</div>
          <p className="mb-2.5 text-[12.5px] text-text-secondary">
            {done.filename} · {(done.size_bytes / 1024).toFixed(1)} KB · {done.artifact_count} artifacts
          </p>
          <div className="flex flex-col gap-2">
            <a href={exportDownloadUrl(done.job_id)} download>
              <Button className="w-full">
                <Download className="h-4 w-4" /> Download ZIP
              </Button>
            </a>
            <Button variant="outline" className="w-full" disabled>
              Open in GitHub (soon)
            </Button>
            <Button variant="ghost" className="w-full" disabled>
              Open in VS Code (soon)
            </Button>
          </div>
        </div>
      ) : (
        <Button onClick={run} disabled={running} className="w-full">
          {running ? "Exporting…" : "Export project"}
        </Button>
      )}

      <div className="rounded-lg border border-line bg-raised p-3">
        <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-text-muted">Export history</div>
        {history.length === 0 ? (
          <p className="text-[12.5px] text-text-muted">No exports yet.</p>
        ) : (
          <ul className="space-y-1.5">
            {history.map((j) => (
              <li key={j.id} className="flex items-center gap-2 text-[12.5px]">
                <span className="h-1.5 w-1.5 rounded-full bg-success" />
                <span className="text-text-secondary">{j.filename}</span>
                <span className="ml-auto font-mono text-[11px] text-text-muted">{(j.size_bytes / 1024).toFixed(1)}KB</span>
                <a href={exportDownloadUrl(j.id)} download className="text-accent" aria-label="Download">
                  <Download className="h-3.5 w-3.5" />
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
