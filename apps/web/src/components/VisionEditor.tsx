"use client";
import { useState } from "react";
import { api, type Vision } from "@/lib/api";

export function VisionEditor({ projectId, initial }: { projectId: string; initial: Vision | null }) {
  const [vision, setVision] = useState<Vision | null>(initial);
  const [content, setContent] = useState(initial?.content ?? "");
  const [busy, setBusy] = useState<"gen" | "save" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setBusy("gen");
    setError(null);
    try {
      const v = await api.generateVision(projectId);
      setVision(v);
      setContent(v.content);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  async function save() {
    setBusy("save");
    setError(null);
    try {
      setVision(await api.saveVision(projectId, content));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <section className="mt-6">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="font-semibold">
          Vision
          {vision && (
            <span className="ml-2 text-xs text-text-muted">
              v{vision.version} · {vision.source}
            </span>
          )}
        </h2>
        <div className="flex gap-2">
          <button
            onClick={generate}
            disabled={!!busy}
            className="rounded-md border border-accent px-3 py-1.5 text-sm text-accent disabled:opacity-50"
          >
            {busy === "gen" ? "Generating…" : vision ? "Regenerate" : "Generate"}
          </button>
          <button
            onClick={save}
            disabled={!!busy || !content.trim()}
            className="rounded-md bg-action px-3 py-1.5 text-sm hover:bg-action-hover disabled:opacity-50"
          >
            {busy === "save" ? "Saving…" : "Save"}
          </button>
        </div>
      </div>
      {error && <p className="mb-2 text-sm text-[#EF4444]">{error}</p>}
      {vision || content ? (
        <textarea
          className="h-96 w-full rounded-md border border-border bg-base p-3 font-mono text-sm"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
      ) : (
        <div className="rounded-md border border-border p-8 text-center text-text-secondary">
          No vision yet. Generate your first.
        </div>
      )}
    </section>
  );
}
