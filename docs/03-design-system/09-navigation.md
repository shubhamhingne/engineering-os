# 09 — Navigation

Navigation is keyboard-first (Principle 4) and maps to the Git-native mental model (Principle 5):
workspace → project → artifact → version.

## Information hierarchy

```
Workspace
└── Project
    ├── Artifacts (Vision, PRD, ADRs, README)
    │   └── Versions (history)
    ├── Runs (generation history)
    └── Repository (linked GitHub repo)
```

The sidebar mirrors this tree; the breadcrumb shows the current path through it.

## Primary navigation (sidebar)

- **Home / Dashboard** — recent projects, activity.
- **Projects** — expandable tree; current project's artifacts inline.
- **Settings** — providers, account, preferences.
- Collapsible to a 56px icon-rail for density.

## Command palette (`⌘K` / `Ctrl+K`)

The fastest path to anything. Required to cover:

- Jump to any project or artifact (fuzzy search).
- Run any primary action ("Generate PRD", "Export repository", "New project").
- Switch provider/model, toggle density, open settings.

Every action surfaced in the palette displays its keyboard shortcut, teaching shortcuts through use.

## Keyboard shortcuts (baseline)

| Action | Shortcut |
|---|---|
| Command palette | `⌘K` |
| New project | `⌘⇧N` |
| Search | `⌘/` |
| Generate (current artifact) | `⌘↵` |
| Save edit | `⌘S` |
| Toggle inspect rail | `⌘I` |
| Next/prev artifact | `⌘]` / `⌘[` |

Shortcuts are discoverable (palette, tooltips) and consistent with editor conventions engineers
already know.

## Breadcrumb

`Workspace / Project / Artifact` — each segment is a navigable link, and the active artifact
segment shows the current version. Provides location and one-click ascent.

## Navigation principles

- **Never trap the user** — Esc closes overlays; breadcrumbs and the palette always offer an exit.
- **State in the URL** — project/artifact/version are routable and shareable (deep links).
- **Don't reinvent gestures** — match GitHub/IDE conventions so the product feels familiar.

## Future evolution

Multi-workspace switching (teams, v3) slots into the existing workspace switcher; the tree and
breadcrumb already accommodate a workspace level, so no navigation redesign is required.
