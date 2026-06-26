"use client";
import { Sparkles } from "lucide-react";
import type { Artifact } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { GenerationTimeline } from "./GenerationTimeline";
import { MetadataInspector } from "./MetadataInspector";
import { TokenCostBadge } from "./TokenCostBadge";

// Right zone: provider, usage, provenance, generation timeline, primary action.
// Token/cost are illustrative until the API surfaces per-run usage on the artifact.
export function AIContextPanel({
  artifact,
  generating,
  onGenerate,
}: {
  artifact: Artifact | null;
  generating: boolean;
  onGenerate: () => void;
}) {
  return (
    <div className="flex h-full flex-col gap-3.5 overflow-auto border-l border-border p-3.5">
      <div className="rounded-lg border border-line bg-raised p-3">
        <div className="mb-2.5 text-[11px] font-semibold uppercase tracking-wide text-text-muted">AI context</div>
        <div className="inline-flex items-center gap-2 rounded-lg border border-line bg-base px-2.5 py-1.5 text-[13px] font-medium">
          <span className="h-3.5 w-3.5 rounded bg-gradient-to-br from-accent to-accent-soft" />
          {artifact?.model ?? "Claude Sonnet 4.6"}
        </div>
      </div>

      <TokenCostBadge tokens={1231} costCents={1.42} />
      <MetadataInspector artifact={artifact} />
      <GenerationTimeline active={generating} current={generating ? 2 : 6} />

      <Button variant="primary" onClick={onGenerate} disabled={generating} className="w-full">
        <Sparkles className="h-4 w-4" />
        {generating ? "Generating…" : artifact ? "Regenerate" : "Generate"}
      </Button>
    </div>
  );
}
