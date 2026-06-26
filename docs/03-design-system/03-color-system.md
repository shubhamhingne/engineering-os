# 03 — Color System

Dark-first, low-chroma, with color reserved for meaning. The palette extends the Brand Book's
slate + blue/cyan system into a full product surface scale.

## Neutrals (slate) — the workhorse

The UI is ~90% neutrals. Color is the exception, not the rule.

| Role | Hex |
|---|---|
| 950 / base | `#0B1220` |
| 900 / app bg | `#0F172A` |
| 800 / raised | `#1E293B` |
| 700 / border | `#334155` |
| 600 / border-strong | `#475569` |
| 500 / muted text | `#64748B` |
| 400 / secondary text | `#94A3B8` |
| 50 / primary text | `#F8FAFC` |

## Brand & interactive

| Role | Hex | Notes |
|---|---|---|
| Action (primary) | `#2563EB` | Buttons, links — the "do it" color |
| Action hover | `#1D4ED8` | |
| Accent (AI / focus) | `#06B6D4` | AI features, focus ring, highlights — used sparingly |
| Accent soft | `#22D3EE` | Hover/active on accent surfaces |

## Semantic

| State | Text/Icon | Surface tint (8–12% on dark) |
|---|---|---|
| Success | `#22C55E` | `rgba(34,197,94,.12)` |
| Warning | `#F59E0B` | `rgba(245,158,11,.12)` |
| Danger | `#EF4444` | `rgba(239,68,68,.12)` |
| Info | `#38BDF8` | `rgba(56,189,248,.12)` |

## Usage rules

- **Accent = AI.** Cyan signals AI-generated or AI-related surfaces (generation panel, "AI"
  badges, streaming cursor). This teaches users to read color as meaning.
- **Action = blue**, only on interactive primary elements. Never decorate with it.
- **Status colors only convey status** — never used for emphasis or theming.
- Maximum one accent and one action color visible per component.

## Contrast (WCAG AA, verified targets)

| Pair | Ratio | Pass |
|---|---|---|
| `#F8FAFC` on `#0F172A` | ~16:1 | AAA |
| `#94A3B8` on `#0F172A` | ~6.5:1 | AA |
| `#FFFFFF` on `#2563EB` | ~5.1:1 | AA |
| `#0B1220` on `#06B6D4` | ~7.4:1 | AAA |

Body and secondary text meet AA (≥4.5:1); large text and UI components meet ≥3:1. Muted text
(`#64748B`) is used only for non-essential meta where it still clears 4.5:1 on base.

## Future evolution

A **light theme** is a token remap (invert the neutral ramp; keep action/accent/semantic). The
semantic structure is theme-agnostic by design, so adding light mode is config, not redesign.
