// Thin API client. The browser never holds secrets; all calls hit the FastAPI backend.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ArtifactType = "vision" | "prd";

export type Project = {
  id: string;
  title: string;
  idea: string;
  artifact_types: string[];
  created_at: string;
  updated_at: string;
};

export type Artifact = {
  type: string;
  version: number;
  source: string;
  content: string;
  model?: string | null;
  created_at: string;
};

export type VersionSummary = {
  version: number;
  source: string;
  model?: string | null;
  created_at: string;
};

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}/api/v1${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail ?? `Request failed (${res.status})`);
  }
  return (await res.json()) as T;
}

export const api = {
  listProjects: () => req<Project[]>("/projects"),
  createProject: (title: string, idea: string) =>
    req<Project>("/projects", { method: "POST", body: JSON.stringify({ title, idea }) }),
  getProject: (id: string) => req<Project>(`/projects/${id}`),

  generateArtifact: (id: string, type: ArtifactType) =>
    req<Artifact>(`/projects/${id}/artifacts/${type}`, { method: "POST" }),
  getArtifact: (id: string, type: ArtifactType) => req<Artifact>(`/projects/${id}/artifacts/${type}`),
  saveArtifact: (id: string, type: ArtifactType, content: string) =>
    req<Artifact>(`/projects/${id}/artifacts/${type}`, { method: "PUT", body: JSON.stringify({ content }) }),
  getVersions: (id: string, type: ArtifactType) =>
    req<VersionSummary[]>(`/projects/${id}/artifacts/${type}/versions`),
};
