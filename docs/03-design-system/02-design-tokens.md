# 02 — Design Tokens

Tokens are the single source of truth for visual values. Components reference tokens, never raw
values. Tokens **inherit from the [Engineering Brand Book §14–16](https://github.com/shubhamhingne/.github)**
(canon: `#0F172A`, `#2563EB`, `#06B6D4`, Inter, JetBrains Mono) and extend them for product UI.

> Implementation note: tokens map to CSS variables and a Tailwind theme (no code here, but the
> naming is chosen to translate 1:1).

## Color (semantic, dark-first)

| Token | Value | Use |
|---|---|---|
| `--surface-base` | `#0F172A` | App background (brand primary) |
| `--surface-raised` | `#1E293B` | Cards, panels |
| `--surface-overlay` | `#273449` | Popovers, menus, command palette |
| `--surface-sunken` | `#0B1220` | Wells, code blocks |
| `--border-subtle` | `#1E293B` | Hairlines |
| `--border-default` | `#334155` | Inputs, dividers |
| `--border-strong` | `#475569` | Emphasis, focused containers |
| `--text-primary` | `#F8FAFC` | Headings, key content |
| `--text-secondary` | `#94A3B8` | Body, labels |
| `--text-muted` | `#64748B` | Meta, hints, disabled |
| `--action` / `--action-hover` | `#2563EB` / `#1D4ED8` | Primary buttons, links |
| `--accent` / `--accent-soft` | `#06B6D4` / `#22D3EE` | AI/focus, highlights (sparingly) |
| `--focus-ring` | `#06B6D4` | Keyboard focus outline |
| `--success` / `--warning` / `--danger` / `--info` | `#22C55E` / `#F59E0B` / `#EF4444` / `#38BDF8` | Status |

Discipline (from the Brand Book): **one element, one blue.** `--action` = interaction,
`--accent` = AI/focus. Never use both for the same job in the same view.

## Spacing — 4px base grid

`0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64` → tokens `space-0 … space-16`. All padding, margin,
and gaps are multiples of 4. See [05 — Spacing & Grid](05-spacing-grid.md).

## Radius

| Token | Value | Use |
|---|---|---|
| `radius-sm` | 6px | Inputs, badges |
| `radius-md` | 8px | Buttons, cards |
| `radius-lg` | 12px | Panels, modals |
| `radius-full` | 9999px | Avatars, pills |

## Elevation

Dark UI signals elevation with **surface + border**, not heavy shadows.

| Token | Composition |
|---|---|
| `elevation-0` | base surface, no border |
| `elevation-1` | `surface-raised` + `border-subtle` |
| `elevation-2` | `surface-overlay` + `border-default` + soft shadow `0 4px 12px rgba(0,0,0,.4)` |

## Typography & motion

Defined in [04 — Typography](04-typography.md) and [10 — Motion](10-motion.md) and referenced as
tokens (`font-*`, `text-*`, `duration-*`, `ease-*`).

## Z-index scale

`base 0 · dropdown 1000 · sticky 1100 · overlay 1200 · modal 1300 · toast 1400 · tooltip 1500`.

## Why tokens

- One change (e.g. accent hue) propagates everywhere — no hunt-and-replace.
- Theming (a future light mode) is a token swap, not a redesign.
- Designers and engineers share one vocabulary, so design and code can't drift.
