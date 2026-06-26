"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Project } from "@/lib/api";
import { NewProjectModal } from "@/components/NewProjectModal";

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setProjects(await api.listProjects());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Projects</h1>
        <NewProjectModal onCreated={load} />
      </div>
      {error && <p className="text-sm text-[#EF4444]">{error} — is the API running on :8000?</p>}
      {loading ? (
        <p className="text-sm text-text-secondary">Loading…</p>
      ) : projects.length === 0 ? (
        <div className="rounded-md border border-border p-8 text-center text-text-secondary">
          No projects yet. Start from an idea.
        </div>
      ) : (
        <ul className="divide-y divide-border rounded-md border border-border">
          {projects.map((p) => (
            <li key={p.id}>
              <Link
                href={`/projects/${p.id}`}
                className="flex items-center justify-between px-4 py-3 hover:bg-raised"
              >
                <span>{p.title}</span>
                <span className="text-xs text-text-muted">
                  {p.artifact_types.length ? p.artifact_types.join(" · ") : "empty"}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
