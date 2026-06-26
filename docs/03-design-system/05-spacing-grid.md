# 05 — Spacing & Grid

A single 4px base unit governs all spacing. Consistency here is what makes an interface feel
engineered rather than assembled.

## Spacing scale (4px base)

| Token | px | Typical use |
|---|---|---|
| `space-1` | 4 | Icon-to-label, tight inline gaps |
| `space-2` | 8 | Within a control, compact stacks |
| `space-3` | 12 | Form field internal padding |
| `space-4` | 16 | Default gap between elements |
| `space-5` | 20 | Card padding |
| `space-6` | 24 | Section gaps |
| `space-8` | 32 | Between major groups |
| `space-10` | 40 | Page section spacing |
| `space-12` | 48 | Large vertical rhythm |
| `space-16` | 64 | Top-level layout gaps |

**Rule:** every gap is a token. No `13px`, no `15px`. If a value isn't on the scale, the layout
is wrong, not the scale.

## Application grid

```
┌───────────┬───────────────────────────────────────────────┐
│  Sidebar  │  Topbar (h: 48)                                │
│  (w: 248) ├───────────────────────────────────────────────┤
│           │  Content (max-w: 1200, padding: 24)            │
│           │   └─ optional right rail (w: 320) for inspect  │
└───────────┴───────────────────────────────────────────────┘
```

- **Sidebar:** fixed 248px (collapsible to 56px icon-rail).
- **Topbar:** 48px height.
- **Content:** centered, max-width 1200px, 24px gutters; fluid below.
- **Right rail (inspect panel):** 320px, appears for generation/inspection (Principle 3).

## Breakpoints

| Token | Min width | Behavior |
|---|---|---|
| `sm` | 640 | Sidebar collapses to icon-rail; right rail becomes a drawer |
| `md` | 768 | Single content column |
| `lg` | 1024 | Sidebar + content |
| `xl` | 1280 | Sidebar + content + right rail |

Primary target is desktop (the work is keyboard-and-screen heavy). Below `md`, the app is usable
but compacted — full mobile is a v2 companion concern, not an MVP layout goal.

## Density

Two density modes (token-driven row heights): **comfortable** (default) and **compact** (power
users, denser tables/lists). Compact reduces row height and vertical padding by one step on the
scale — never font size, to preserve readability.
