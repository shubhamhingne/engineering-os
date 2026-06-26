# 06 — Iconography

Icons are functional wayfinding, not decoration. One library, one weight, consistent sizing.

## Library

**Lucide** (inherited from the Brand Book) — open-source, line icons, consistent geometry,
React-ready. Single library only; no mixing icon sets (a common source of visual drift).

## Sizing

| Token | Size | Use |
|---|---|---|
| `icon-sm` | 14 | Inline with `small`/`caption` text, dense rows |
| `icon-md` | 16 | Default — buttons, menu items, with `body` text |
| `icon-lg` | 20 | Section headers, empty states |
| `icon-xl` | 24 | Feature/empty-state focal icons |

Stroke width: **1.5px** everywhere (Lucide default), `2px` only for `icon-xl` focal use.

## Color rules

- Icons inherit text color by default (`currentColor`) — secondary text color in most UI.
- **Accent (cyan) only on AI-related icons** (generation, model, sparkle/AI badge) — color
  carries meaning (see [03 — Color System](03-color-system.md)).
- Status icons use their semantic color (success/warning/danger/info).
- Never multicolor or filled icons; line-only for consistency.

## Semantic icon vocabulary

A shared mapping so the same concept always uses the same glyph:

| Concept | Icon (Lucide) |
|---|---|
| Project | `folder-git-2` |
| Artifact | `file-text` |
| ADR / decision | `git-commit-horizontal` |
| Generation / AI | `sparkles` |
| Provider / model | `cpu` |
| Repository | `github` |
| Version history | `history` |
| Cost / tokens | `gauge` |
| Settings | `settings-2` |
| Command palette | `command` |

## Accessibility

- Icon-only controls **must** have an `aria-label` and a tooltip ([11 — Accessibility](11-accessibility.md)).
- Icons that convey state are paired with text or a status color, never color alone.

## Why line icons at one weight

Mixed weights and styles read as inconsistency — the opposite of the "engineered" feel. A single
line set at 1.5px sits quietly beside Inter and never competes with content (Principle 6).
