import type { Artifact } from "@/lib/api";

// Artifact provenance — trust through transparency (Principle 3). Pure.
export function MetadataInspector({ artifact }: { artifact: Artifact | null }) {
  const rows: [string, string][] = [
    ["Model", artifact?.model ?? "—"],
    ["Source", artifact?.source ?? "—"],
    ["Version", artifact ? `v${artifact.version}` : "—"],
    ["Type", artifact?.type ?? "—"],
  ];
  return (
    <div className="rounded-lg border border-line bg-raised p-3">
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-text-muted">Provenance</div>
      {rows.map(([key, value]) => (
        <div key={key} className="flex justify-between py-1 text-[12.5px]">
          <span className="text-text-muted">{key}</span>
          <span className="font-mono text-text-secondary">{value}</span>
        </div>
      ))}
    </div>
  );
}
