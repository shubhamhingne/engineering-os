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
    <div className="min-h-screen">
      <header className="flex h-12 items-center gap-3 border-b border-border px-4">
        <span className="text-sm font-semibold">Engineering OS</span>
        <span className="text-[13px] text-text-muted">Idea → repository</span>
      </header>
      <main className="mx-auto max-w-4xl px-6 py-8">
        <div className="mb-5 flex items-center">
          <div>
            <h1 className="text-xl font-semibold">Projects</h1>
            <p className="text-[13px] text-text-muted">Idea to repository</p>
          </div>
          <div className="ml-auto">
            <NewProjectModal onCreated={load} />
          </div>
        </div>

        {error && <p className="text-sm text-danger">{error} — is the API running on :8000?</p>}

        {loading ? (
          <p className="text-sm text-text-secondary">Loading…</p>
        ) : projects.length === 0 ? (
          <div className="rounded-xl border border-dashed border-line p-10 text-center">
            <p className="font-medium">Start from an idea</p>
            <p className="mt-1 text-[13px] text-text-muted">
              Create your first project and generate a Vision in seconds.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <Link
                key={p.id}
                href={`/projects/${p.id}`}
                className="flex min-h-[128px] flex-col rounded-xl border border-line bg-raised p-4 transition-colors hover:border-[#3f516b]"
              >
                <div className="font-semibold">{p.title}</div>
                <div className="mt-1.5 flex-1 text-[12.5px] leading-5 text-text-secondary">{p.idea}</div>
                <div className="mt-3 flex gap-1.5">
                  {p.artifact_types.length ? (
                    p.artifact_types.map((t) => (
                      <span key={t} className="rounded-full border border-line px-2 py-0.5 font-mono text-[10.5px] text-text-secondary">
                        {t}
                      </span>
                    ))
                  ) : (
                    <span className="rounded-full border border-line px-2 py-0.5 font-mono text-[10.5px] text-text-muted">empty</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
