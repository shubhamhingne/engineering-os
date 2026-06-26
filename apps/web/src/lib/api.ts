// Thin API client. The browser never holds secrets; all calls hit the FastAPI backend.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Project = {
  id: string;
  title: string;
  idea: string;
  has_vision: boolean;
  created_at: string;
  updated_at: string;
};

export type Vision = {
  content: string;
  source: string;
  version: number;
  model?: string | null;
  updated_at: string;
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
  generateVision: (id: string) => req<Vision>(`/projects/${id}/vision`, { method: "POST" }),
  getVision: (id: string) => req<Vision>(`/projects/${id}/vision`),
  saveVision: (id: string, content: string) =>
    req<Vision>(`/projects/${id}/vision`, { method: "PUT", body: JSON.stringify({ content }) }),
};
