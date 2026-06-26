import { lineDiff } from "@/lib/diff";
import { cn } from "@/lib/cn";

// Line diff between the saved version and the current draft. Pure.
export function DiffViewer({ before, after }: { before: string; after: string }) {
  const lines = lineDiff(before, after);
  return (
    <div className="px-10 py-6 font-mono text-[12.5px] leading-6">
      {lines.map((line, i) => (
        <div
          key={i}
          className={cn(
            "px-1",
            line.type === "add" && "bg-success/10 text-success",
            line.type === "del" && "bg-danger/10 text-danger",
            line.type === "same" && "text-text-secondary",
          )}
        >
          <span className="mr-3 select-none text-text-muted">
            {line.type === "add" ? "+" : line.type === "del" ? "−" : " "}
          </span>
          {line.text || " "}
        </div>
      ))}
    </div>
  );
}
