"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Search, Sparkles } from "lucide-react";
import { api, streamArtifact, type ArtifactType, type ReadmeQuality } from "@/lib/api";
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
import { CommandPalette, type Command } from "./CommandPalette";
import { ExportPanel } from "./ExportPanel";

const LABEL: Record<string, string> = { vision: "Vision", prd: "PRD", readme: "README", adr: "ADR" };
const EMPTY: Record<string, string> = {
  vision: "Generate a Vision from your idea to start the lifecycle.",
  prd: "Generate your first Product Requirements Document — it will be created from your approved Vision.",
  readme: "Generate a README once your artifacts are ready.",
  adr: "Record your first architecture decision.",
};
const STAGE_INDEX: Record<string, number> = {
  building_context: 0,
  selecting_prompt: 1,
  calling_model: 2,
  formatting: 4,
  saved: 5,
};

export function WorkspaceShell({ projectId }: { projectId: string }) {
  const ws = useWorkspace(projectId);
  const router = useRouter();
  const [view, setView] = useState<ViewMode>("markdown");
  const [draft, setDraft] = useState("");
  const [dirty, setDirty] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [stage, setStage] = useState(6);
  const [actionError, setActionError] = useState<string | null>(null);
  const [exportMode, setExportMode] = useState(false);
  const [quality, setQuality] = useState<ReadmeQuality | null>(null);

  useEffect(() => {
    if (ws.type === "readme" && ws.artifact) {
      api.readmeQuality(projectId).then(setQuality).catch(() => setQuality(null));
    } else {
      setQuality(null);
    }
  }, [ws.type, ws.artifact, projectId]);

  const saved = ws.artifact?.content ?? "";

  useEffect(() => {
    if (!generating) {
      setDraft(saved);
      setDirty(false);
    }
  }, [saved, ws.type, generating]);

  async function handleGenerate(type: ArtifactType = ws.type) {
    // README and ADR are synthesized (deterministic), not streamed.
    if (type === "readme" || type === "adr") {
      setGenerating(true);
      setActionError(null);
      try {
        await api.generateArtifact(projectId, type);
        await ws.selectType(type);
      } catch (e) {
        setActionError((e as Error).message);
      } finally {
        setGenerating(false);
      }
      return;
    }
    if (type !== ws.type) await ws.selectType(type);
    setGenerating(true);
    setActionError(null);
    setStage(0);
    setDraft("");
    setView("markdown");
    try {
      await streamArtifact(projectId, type, {
        onStage: (s) => setStage(STAGE_INDEX[s] ?? 3),
        onToken: (t) => {
          setStage(3);
          setDraft((d) => d + t);
        },
        onDone: async () => {
          setStage(6);
          await ws.reload();
          setDirty(false);
        },
        onError: (d) => setActionError(d),
      });
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

  // ⌘S to save
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        if (dirty && draft.trim()) void handleSave();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }); // re-bind each render so it sees current draft/dirty

  const commands: Command[] = [
    { id: "home", label: "Go to Projects", group: "Navigate", shortcut: "⌘H", run: () => router.push("/") },
    { id: "gen-vision", label: "Generate Vision", group: "Actions", run: () => void handleGenerate("vision") },
    { id: "gen-prd", label: "Generate PRD", group: "Actions", run: () => void handleGenerate("prd") },
    { id: "gen-readme", label: "Generate README", group: "Actions", run: () => void handleGenerate("readme") },
    { id: "gen-adr", label: "Generate ADR", group: "Actions", run: () => void handleGenerate("adr") },
    { id: "save", label: "Save artifact", group: "Actions", shortcut: "⌘S", enabled: dirty, run: () => void handleSave() },
    { id: "export", label: "Export project", group: "Actions", run: () => setExportMode(true) },
    { id: "open-vision", label: "Open Vision", group: "Artifacts", run: () => void ws.selectType("vision") },
    { id: "open-prd", label: "Open PRD", group: "Artifacts", run: () => void ws.selectType("prd") },
  ];

  const banner = actionError ?? ws.error;

  return (
    <div className="grid h-screen grid-rows-[48px_minmax(0,1fr)_168px] bg-base text-text">
      <CommandPalette commands={commands} />

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
        <Button size="sm" variant="outline" onClick={() => setExportMode(true)}>
          Export
        </Button>
        <div className="h-6 w-6 rounded-full bg-gradient-to-br from-action to-accent" aria-hidden />
      </header>

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
              <motion.span
                key={ws.artifact.version}
                initial={{ scale: 0.9, opacity: 0.6 }}
                animate={{ scale: 1, opacity: 1 }}
                className="rounded-full border border-line px-2 py-0.5 font-mono text-[11px] text-text-secondary"
              >
                v{ws.artifact.version} · {ws.artifact.source}
              </motion.span>
            )}
            {ws.type === "readme" && quality && (
              <span
                title={`Missing: ${quality.missing.join(", ") || "nothing"}`}
                className="rounded-full border border-accent/40 px-2 py-0.5 font-mono text-[11px] text-accent"
              >
                README {quality.score}/100
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
            ) : !ws.artifact && !draft && !generating ? (
              <div className="grid h-full place-items-center px-10 text-center">
                <div className="max-w-sm">
                  <Sparkles className="mx-auto mb-3 h-6 w-6 text-accent" />
                  <p className="font-medium text-text">No {LABEL[ws.type]} yet</p>
                  <p className="mt-1 text-[13px] text-text-secondary">{EMPTY[ws.type]}</p>
                  <Button variant="outline" className="mt-4" onClick={() => handleGenerate()} disabled={generating}>
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
          {exportMode ? (
            <ExportPanel projectId={projectId} onClose={() => setExportMode(false)} />
          ) : (
            <AIContextPanel
              artifact={ws.artifact}
              generating={generating}
              stage={stage}
              onGenerate={() => handleGenerate()}
            />
          )}
        </aside>
      </div>

      <BottomActivityPanel versions={ws.versions} />
    </div>
  );
}
