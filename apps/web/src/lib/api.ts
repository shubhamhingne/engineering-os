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

export type StreamDone = { version: number; tokens_out: number; latency_ms: number; model?: string | null };

export type StreamHandlers = {
  onStage?: (stage: string) => void;
  onToken?: (text: string) => void;
  onDone?: (data: StreamDone) => void;
  onError?: (detail: string) => void;
};

// Streamed generation (SSE over fetch). Tokens arrive live; the artifact "grows".
export async function streamArtifact(id: string, type: ArtifactType, h: StreamHandlers): Promise<void> {
  const res = await fetch(`${BASE}/api/v1/projects/${id}/artifacts/${type}/stream`, { method: "POST" });
  if (!res.ok || !res.body) {
    const body = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail ?? `Request failed (${res.status})`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      const event = chunk.match(/event: (\w+)/)?.[1];
      const dataLine = chunk.split("\n").find((l) => l.startsWith("data: "))?.slice(6);
      if (!event || !dataLine) continue;
      const data = JSON.parse(dataLine);
      if (event === "stage") h.onStage?.(data.stage);
      else if (event === "token") h.onToken?.(data.text);
      else if (event === "done") h.onDone?.(data);
      else if (event === "error") h.onError?.(data.detail);
    }
  }
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
  listExports: (id: string) => req<ExportJob[]>(`/projects/${id}/exports`),
};

export type ExportJob = {
  id: string;
  status: string;
  filename: string;
  size_bytes: number;
  artifact_count: number;
  created_at: string;
};

export type ExportDone = { job_id: string; filename: string; size_bytes: number; artifact_count: number };

export type ExportHandlers = {
  onPhase?: (phase: string) => void;
  onDone?: (data: ExportDone) => void;
  onError?: (detail: string) => void;
};

// Streamed export pipeline — reuses the same SSE pattern as generation.
export async function streamExport(id: string, h: ExportHandlers): Promise<void> {
  const res = await fetch(`${BASE}/api/v1/projects/${id}/export/stream`, { method: "POST" });
  if (!res.ok || !res.body) {
    const body = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail ?? `Request failed (${res.status})`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      const event = chunk.match(/event: (\w+)/)?.[1];
      const dataLine = chunk.split("\n").find((l) => l.startsWith("data: "))?.slice(6);
      if (!event || !dataLine) continue;
      const data = JSON.parse(dataLine);
      if (event === "phase") h.onPhase?.(data.phase);
      else if (event === "done") h.onDone?.(data);
      else if (event === "error") h.onError?.(data.detail);
    }
  }
}

export const exportDownloadUrl = (jobId: string): string => `${BASE}/api/v1/exports/${jobId}/download`;
