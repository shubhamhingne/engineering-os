"use client";
import { useEffect, useState } from "react";
import { api, type Artifact, type ArtifactType, type VersionSummary } from "@/lib/api";

// One editor for every artifact type (Vision, PRD, …). No per-type duplication.
export function ArtifactEditor({
  projectId,
  type,
  label,
}: {
  projectId: string;
  type: ArtifactType;
  label: string;
}) {
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [content, setContent] = useState("");
  const [versions, setVersions] = useState<VersionSummary[]>([]);
  const [busy, setBusy] = useState<"gen" | "save" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function refreshVersions() {
    try {
      setVersions(await api.getVersions(projectId, type));
    } catch {
      /* none yet */
    }
  }

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const a = await api.getArtifact(projectId, type);
        if (active) {
          setArtifact(a);
          setContent(a.content);
        }
      } catch {
        if (active) {
          setArtifact(null);
          setContent("");
        }
      }
      await refreshVersions();
      if (active) setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [projectId, type]);

  async function generate() {
    setBusy("gen");
    setError(null);
    try {
      const a = await api.generateArtifact(projectId, type);
      setArtifact(a);
      setContent(a.content);
      await refreshVersions();
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
      setArtifact(await api.saveArtifact(projectId, type, content));
      await refreshVersions();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  if (loading) return <p className="mt-6 text-sm text-text-secondary">Loading…</p>;

  return (
    <section className="mt-6">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="font-semibold">
          {label}
          {artifact && (
            <span className="ml-2 text-xs text-text-muted">
              v{artifact.version} · {artifact.source}
            </span>
          )}
        </h2>
        <div className="flex gap-2">
          <button
            onClick={generate}
            disabled={!!busy}
            className="rounded-md border border-accent px-3 py-1.5 text-sm text-accent disabled:opacity-50"
          >
            {busy === "gen" ? "Generating…" : artifact ? "Regenerate" : "Generate"}
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
      <div className="grid grid-cols-[1fr_180px] gap-4">
        {artifact || content ? (
          <textarea
            className="h-96 w-full rounded-md border border-border bg-base p-3 font-mono text-sm"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        ) : (
          <div className="rounded-md border border-border p-8 text-center text-text-secondary">
            No {label} yet. Generate your first.
          </div>
        )}
        <aside>
          <h3 className="mb-2 text-xs uppercase tracking-wide text-text-muted">Version history</h3>
          {versions.length === 0 ? (
            <p className="text-sm text-text-muted">No versions yet.</p>
          ) : (
            <ul className="space-y-1">
              {versions.map((v) => (
                <li
                  key={v.version}
                  className="flex items-center justify-between rounded border border-border px-2 py-1 text-xs"
                >
                  <span>v{v.version}</span>
                  <span className="text-text-muted">{v.source}</span>
                </li>
              ))}
            </ul>
          )}
        </aside>
      </div>
    </section>
  );
}
