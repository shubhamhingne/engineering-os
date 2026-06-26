"use client";

// Controlled Markdown editor surface. Pure: value in, change out.
export function ArtifactEditor({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      spellCheck={false}
      aria-label="Artifact markdown editor"
      className="h-full w-full resize-none bg-base px-10 py-6 font-mono text-[13px] leading-6 text-text-body outline-none"
    />
  );
}
