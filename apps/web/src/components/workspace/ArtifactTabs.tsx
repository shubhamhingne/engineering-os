"use client";
import * as Tabs from "@radix-ui/react-tabs";

export type ViewMode = "markdown" | "preview" | "diff";

const MODES: ViewMode[] = ["markdown", "preview", "diff"];

// View-mode tabs on Radix — keyboard + ARIA for free (a11y by construction).
export function ArtifactTabs({ value, onChange }: { value: ViewMode; onChange: (v: ViewMode) => void }) {
  return (
    <Tabs.Root value={value} onValueChange={(v) => onChange(v as ViewMode)}>
      <Tabs.List className="flex overflow-hidden rounded-md border border-line" aria-label="View mode">
        {MODES.map((m) => (
          <Tabs.Trigger
            key={m}
            value={m}
            className={
              "px-3 py-1.5 text-xs capitalize text-text-secondary " +
              "data-[state=active]:bg-raised data-[state=active]:text-text " +
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            }
          >
            {m}
          </Tabs.Trigger>
        ))}
      </Tabs.List>
    </Tabs.Root>
  );
}
