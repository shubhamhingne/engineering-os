"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search } from "lucide-react";
import type { ArtifactType } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { fadeRise } from "@/lib/motion";
import { useWorkspace } from "./useWorkspace";
import { ArtifactTree } from "./ArtifactTree";
import { ArtifactTabs, type ViewMode } from "./ArtifactTabs";
import { ArtifactEditor } from "./ArtifactEditor";
import { MarkdownPreview } from "./MarkdownPreview";
import { DiffViewer } from "./DiffViewer";
import { AIContextPanel } from "./AIContextPanel";
import { BottomActivityPanel } from "./BottomActivityPanel";

const LABEL: Record<string, string> = { vision: "Vision", prd: "PRD", readme: "README", adr: "ADR" };

// The signature screen: composes the four zones. One shell, many artifact capabilities.
export function WorkspaceShell({ projectId }: { projectId: string }) {
  const ws = useWorkspace(projectId);
  const [view, setView] = useState<ViewMode>("markdown");
  const [draft, setDraft] = useState("");
  const [dirty, setDirty] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const saved = ws.artifact?.content ?? "";

  // Reset the draft when the loaded artifact (or active type) changes.
  useEffect(() => {
    setDraft(saved);
    setDirty(false);
  }, [saved, ws.type]);

  async function handleGenerate() {
    setGenerating(true);
    setActionError(null);
    try {
      await ws.generate();
    } catch (e) {
      setActionError((e as Error).message);
    } finally {
      setGenerating(false);
    }
  }

  async function handleSave() {
    setActionError(null);
    try {
      await ws.save(draft);
    } catch (e) {
      setActionError((e as Error).message);
    }
  }

  const banner = actionError ?? ws.error;

  return (
    <div className="grid h-screen grid-rows-[48px_minmax(0,1fr)_168px] bg-base text-text">
      {/* GLOBAL NAV */}
      <header className="flex items-center gap-3.5 border-b border-border px-4">
        <Link href="/" className="text-sm font-semibold">
          Engineering OS
        </Link>
        <span className="text-[13px] text-text-secondary">
          / <b className="text-text">{ws.project?.title ?? "…"}</b> / {LABEL[ws.type]}
        </span>
        <div className="ml-auto flex w-72 items-center gap-2 rounded-md border border-line bg-raised px-2.5 py-1.5 text-[13px] text-text-muted">
          <Search className="h-3.5 w-3.5" /> Search or run a command
          <kbd className="ml-auto rounded border border-line px-1.5 font-mono text-[11px]">⌘K</kbd>
        </div>
        <div className="h-6 w-6 rounded-full bg-gradient-to-br from-action to-accent" aria-hidden />
      </header>

      {/* MAIN — three zones */}
      <div className="grid grid-cols-[236px_minmax(0,1fr)_320px] overflow-hidden">
        <aside className="overflow-auto border-r border-border">
          <ArtifactTree
            active={ws.type}
            present={ws.project?.artifact_types ?? []}
            onSelect={(t: ArtifactType) => void ws.selectType(t)}
          />
        </aside>

        <section className="flex min-w-0 flex-col">
          <div className="flex items-center gap-3 border-b border-border px-5 py-3">
            <span className="font-semibold">{LABEL[ws.type]}</span>
            {ws.artifact && (
              <span className="rounded-full border border-line px-2 py-0.5 font-mono text-[11px] text-text-secondary">
                v{ws.artifact.version} · {ws.artifact.source}
              </span>
            )}
            <div className="ml-auto flex items-center gap-2">
              <ArtifactTabs value={view} onChange={setView} />
              <Button size="sm" onClick={handleSave} disabled={!dirty || !draft.trim()}>
                Save
              </Button>
            </div>
          </div>

          {banner && (
            <div className="border-b border-danger/30 bg-danger/10 px-5 py-2 text-[13px] text-danger" role="alert">
              {banner}
            </div>
          )}

          <motion.div
            key={`${ws.type}-${view}`}
            variants={fadeRise}
            initial="hidden"
            animate="show"
            className="min-h-0 flex-1 overflow-auto"
          >
            {ws.loading ? (
              <p className="px-10 py-6 text-sm text-text-secondary">Loading…</p>
            ) : !ws.artifact && !draft ? (
              <div className="grid h-full place-items-center px-10 text-center">
                <div>
                  <p className="text-text-secondary">No {LABEL[ws.type]} yet.</p>
                  <Button variant="outline" className="mt-3" onClick={handleGenerate} disabled={generating}>
                    Generate {LABEL[ws.type]}
                  </Button>
                </div>
              </div>
            ) : view === "preview" ? (
              <MarkdownPreview content={draft} />
            ) : view === "diff" ? (
              <DiffViewer before={saved} after={draft} />
            ) : (
              <ArtifactEditor
                value={draft}
                onChange={(v) => {
                  setDraft(v);
                  setDirty(true);
                }}
              />
            )}
          </motion.div>
        </section>

        <aside className="overflow-hidden">
          <AIContextPanel artifact={ws.artifact} generating={generating} onGenerate={handleGenerate} />
        </aside>
      </div>

      {/* BOTTOM */}
      <BottomActivityPanel versions={ws.versions} />
    </div>
  );
}
