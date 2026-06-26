"use client";
import { useCallback, useEffect, useState } from "react";
import { api, type Artifact, type ArtifactType, type Project, type VersionSummary } from "@/lib/api";

// The single I/O seam: owns server state and mutations, isolated from presentation (EDR-001).
export function useWorkspace(projectId: string) {
  const [project, setProject] = useState<Project | null>(null);
  const [type, setType] = useState<ArtifactType>("vision");
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [versions, setVersions] = useState<VersionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadArtifact = useCallback(
    async (t: ArtifactType) => {
      try {
        setArtifact(await api.getArtifact(projectId, t));
      } catch {
        setArtifact(null);
      }
      try {
        setVersions(await api.getVersions(projectId, t));
      } catch {
        setVersions([]);
      }
    },
    [projectId],
  );

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      try {
        const p = await api.getProject(projectId);
        if (active) setProject(p);
      } catch (e) {
        if (active) setError((e as Error).message);
      }
      await loadArtifact("vision");
      if (active) setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [projectId, loadArtifact]);

  const selectType = useCallback(
    async (t: ArtifactType) => {
      setType(t);
      await loadArtifact(t);
    },
    [loadArtifact],
  );

  const generate = useCallback(async () => {
    const a = await api.generateArtifact(projectId, type);
    setArtifact(a);
    setVersions(await api.getVersions(projectId, type));
    try {
      setProject(await api.getProject(projectId));
    } catch {
      /* keep current project */
    }
    return a;
  }, [projectId, type]);

  const save = useCallback(
    async (content: string) => {
      const a = await api.saveArtifact(projectId, type, content);
      setArtifact(a);
      setVersions(await api.getVersions(projectId, type));
      return a;
    },
    [projectId, type],
  );

  const reload = useCallback(async () => {
    await loadArtifact(type);
    try {
      setProject(await api.getProject(projectId));
    } catch {
      /* keep current project */
    }
  }, [loadArtifact, type, projectId]);

  return { project, type, artifact, versions, loading, error, selectType, generate, save, reload };
}
