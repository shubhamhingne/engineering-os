"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { api, type Project, type Vision } from "@/lib/api";
import { VisionEditor } from "@/components/VisionEditor";

export default function ProjectDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [project, setProject] = useState<Project | null>(null);
  const [vision, setVision] = useState<Vision | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const p = await api.getProject(id);
        setProject(p);
        if (p.has_vision) {
          try {
            setVision(await api.getVision(id));
          } catch {
            /* no vision yet */
          }
        }
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
      <VisionEditor projectId={id} initial={vision} />
    </div>
  );
}
