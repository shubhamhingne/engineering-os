# 08 — Layout System

One consistent app shell, three content patterns. Predictable layout is what lets users build
muscle memory — they always know where things are.

## App shell

```
┌──────────┬──────────────────────────────────────────────┐
│          │  Topbar: breadcrumb · search(⌘K) · user       │
│ Sidebar  ├──────────────────────────────────────────────┤
│          │                                               │
│ • Home   │   Content region                              │
│ • Project│   (one of the three patterns below)           │
│   tree   │                                               │
│          │                          ┌── Inspect rail ──┐ │
│ • Settings                          │ prompt · tokens  │ │
│          │                          │ cost · provider  │ │
└──────────┴──────────────────────────┴──────────────────┘
```

- **Sidebar (248px / 56px rail):** workspace + project navigation, persistent.
- **Topbar (48px):** breadcrumb (location), command/search, account.
- **Inspect rail (320px):** optional right panel for AI provenance and version history
  (Principle 3). Toggled with a shortcut; a drawer on small screens.

## Three content patterns

1. **List view** — projects, artifacts, runs. Dense rows, sortable, keyboard-navigable; empty
   and loading states required ([12](12-empty-loading-error-states.md)).
2. **Detail view** — a single project or artifact. Header + primary content + contextual actions.
3. **Workspace (editor) view** — the artifact editor with the generation panel and inspect rail.
   The product's center of gravity.

## Responsiveness

| Width | Layout |
|---|---|
| ≥ 1280 (`xl`) | Sidebar + content + inspect rail |
| 1024–1279 (`lg`) | Sidebar + content; inspect rail as overlay |
| 768–1023 (`md`) | Sidebar collapses to icon-rail; single column |
| < 768 | Compacted, read/review oriented (full editing is desktop-first) |

## Layout rules

- Max content width 1200px; never full-bleed text (hurts readability, Principle 1).
- The shell never moves — only the content region changes. Navigation is stable across the app.
- Scroll is contained to the content region; sidebar and topbar are fixed.
- One primary action per view, visually distinct (`--action`); secondary actions are quieter.

## Why one shell

A stable shell with predictable regions is calm (Principle 6) and learnable. Products that
restructure their chrome per screen force users to re-orient constantly; we refuse that. The
content changes; the frame does not.
