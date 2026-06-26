"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { api, type Project } from "@/lib/api";
import { ArtifactEditor } from "@/components/ArtifactEditor";

const TABS = [
  { key: "vision", label: "Vision" },
  { key: "prd", label: "PRD" },
  { key: "activity", label: "Activity" },
] as const;

type Tab = (typeof TABS)[number]["key"];

export default function ProjectDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<Tab>("vision");

  useEffect(() => {
    (async () => {
      try {
        setProject(await api.getProject(id));
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setReady(true);
      }
    })();
  }, [id]);

  if (!ready) return <p className="text-sm text-text-secondary">Loading…</p>;
  if (error || !project) return <p className="text-sm text-[#EF4444]">{error ?? "Not found"}</p>;

  return (
    <div>
      <Link href="/" className="text-sm text-text-secondary">
        ← Projects
      </Link>
      <h1 className="mt-2 text-xl font-semibold">{project.title}</h1>
      <p className="mt-1 text-sm text-text-secondary">{project.idea}</p>

      <nav className="mt-4 flex gap-1 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={
              tab === t.key
                ? "border-b-2 border-accent px-3 py-2 text-sm text-text"
                : "px-3 py-2 text-sm text-text-secondary"
            }
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "vision" && <ArtifactEditor projectId={id} type="vision" label="Vision" />}
      {tab === "prd" && <ArtifactEditor projectId={id} type="prd" label="PRD" />}
      {tab === "activity" && (
        <div className="mt-6 rounded-md border border-border p-8 text-center text-text-secondary">
          Activity — coming soon.
        </div>
      )}
    </div>
  );
}
