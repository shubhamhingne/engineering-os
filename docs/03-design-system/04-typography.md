# 04 — Typography

Two families, inherited from the Brand Book: **Inter** for everything human-readable,
**JetBrains Mono** for code, IDs, tokens, and metrics. No third family.

## Type scale (Inter)

A modular scale tuned for density. Sizes in px / line-height / weight.

| Token | Size | Line-height | Weight | Use |
|---|---|---|---|---|
| `display` | 30 | 36 | 600 | Page titles (rare) |
| `h1` | 24 | 32 | 600 | Screen headings |
| `h2` | 20 | 28 | 600 | Section headings |
| `h3` | 16 | 24 | 600 | Card/group headings |
| `body` | 14 | 22 | 400 | Default UI text |
| `body-strong` | 14 | 22 | 500 | Emphasis, labels |
| `small` | 13 | 20 | 400 | Secondary info |
| `caption` | 12 | 16 | 500 | Meta, badges, hints |

> 14px is the workhorse body size — dense without straining, standard for engineer-facing SaaS
> (Linear, GitHub). 16px is reserved for long-form reading surfaces (the Markdown editor).

## Monospace (JetBrains Mono)

| Token | Size | Use |
|---|---|---|
| `code` | 13 | Inline code, IDs, tokens |
| `code-block` | 13 / 20 | Code blocks, diffs, logs |
| `metric` | 13 | Token counts, cost, latency (tabular numerals on) |

Enable `font-variant-numeric: tabular-nums` for all metrics so numbers align in columns.

## Rules

- **Tracking:** tighten headings slightly (`-0.01em`); body default.
- **Hierarchy by weight and color first, size second** — keeps the dense UI calm (Principle 6).
- **Max line length** for reading surfaces: ~72ch (the Markdown editor constrains measure).
- **No italics for UI**; reserve italics for quoted/draft content.
- Long-form artifact content uses the 16px reading scale with generous line-height (26px).

## Why this scale

Engineer tools live or die on scannability. A compact scale with strong weight contrast packs
more on screen without noise, and the mono family makes machine data (cost, tokens, IDs)
instantly distinguishable from prose — reinforcing "everything is inspectable" (Principle 3).
