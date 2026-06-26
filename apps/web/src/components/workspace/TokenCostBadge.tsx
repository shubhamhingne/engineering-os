// Live token + cost meter (mono, tabular). Pure presentational.
export function TokenCostBadge({ tokens, costCents }: { tokens: number; costCents: number }) {
  return (
    <div className="rounded-lg border border-line bg-raised p-3">
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-text-muted">AI usage</div>
      <div className="flex items-baseline justify-between tabular-nums">
        <span className="font-mono text-[22px] text-text">{tokens.toLocaleString()}</span>
        <span className="font-mono text-[15px] text-accent-soft">${(costCents / 100).toFixed(4)}</span>
      </div>
      <div className="flex items-baseline justify-between text-[11px] text-text-muted">
        <span>tokens</span>
        <span>est. cost</span>
      </div>
      <div className="mt-2 h-[5px] overflow-hidden rounded bg-sunken">
        <div className="h-full rounded bg-gradient-to-r from-action to-accent" style={{ width: "62%" }} />
      </div>
    </div>
  );
}
