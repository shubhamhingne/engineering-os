# 18 — Engineering Workspace Design Spec

The high-fidelity design for the signature screen and the full frame set (Day 10.5 design
sprint). This is **Product Experience Design**, not styling — information architecture and
interaction first. Built to the [UI/UX Pro Max](17-ui-ux-pro-max.md) standard.

> **Verified mockups** (rendered, in `design/mockups/` → `docs/06-media/screenshots/`):
> [Artifact Workspace](../06-media/screenshots/artifact-workspace.png) ·
> [Dashboard](../06-media/screenshots/dashboard.png) ·
> [Command Palette](../06-media/screenshots/command-palette.png).
> The mockups are self-contained HTML/CSS — they double as the pixel spec for implementation.

## Composition rule: 70 / 20 / 10

**70% content · 20% structure · 10% decoration.** Most AI apps invert this. Content (the
artifact) dominates; structure (zones, borders) is quiet; decoration is minimal and functional.

## The four-zone workspace

Everything important stays visible — no hidden drawers, no modal overload.

```
┌────────────────────────────────────────────────────────────┐
│ Global navigation · breadcrumb · ⌘K · account              │
├──────────────┬───────────────────────┬─────────────────────┤
│ Artifact tree│ Artifact workspace    │ AI context          │
│ Vision  PRD  │ Markdown · Preview ·   │ provider · token    │
│ README  ADR  │ Diff (version-aware)  │ meter · cost ·      │
│ Tasks  Arch. │                       │ provenance · gen    │
│              │                       │ timeline · actions  │
├──────────────┴───────────────────────┴─────────────────────┤
│ Version timeline · Activity · Logs                         │
└────────────────────────────────────────────────────────────┘
```

- **Left** — typed artifact tree (ADR-0004), status dots (AI=cyan, done=green).
- **Center** — editor with **Markdown / Preview / Diff** segmented control; diff on version switch.
- **Right** — AI context: provider chip, live **token meter + cost**, provenance, generation timeline.
- **Bottom** — version timeline (v4 Human · v3 Claude · …) + activity feed.

## Frame set (20)

| # | Frame | Inspiration | Key elements / states |
|---|---|---|---|
| 1 | Landing Dashboard | Linear | Projects, search, account |
| 2 | Projects Grid | Linear | Cards: title, artifact chips, lifecycle progress |
| 3 | New Project Dialog | Vercel | Title + idea, validation, primary CTA |
| 4 | Artifact Workspace (default) | Cursor/Notion | The four-zone layout |
| 5 | Vision Generation (loading) | Cursor | Live generation timeline, streaming, token ticker |
| 6 | Vision Complete | Notion | Rendered artifact, provenance populated |
| 7 | PRD | Notion | Same workspace, PRD tab, generated from Vision |
| 8 | Version History | GitHub | Bottom timeline; select a version |
| 9 | Diff Viewer | GitHub | Side-by-side / inline diff between versions |
| 10 | Prompt Inspector | Cursor | Prompt version + body, editable |
| 11 | AI Provider Details | Vercel | Model, limits, cost tier, connect/disconnect |
| 12 | Export Repository | GitHub | Scaffold preview, name, visibility, create |
| 13 | Command Palette | Raycast | Fuzzy search, grouped actions, shortcuts |
| 14 | Settings | Vercel | Providers, preferences, grouped sections |
| 15 | Empty State | Linear | Value + CTA + subtle cue (not "no data") |
| 16 | Error State | Linear | Calm, specific, recoverable, "work is safe" |
| 17 | Mobile Responsive | — | Zones collapse to stacked review layout |
| 18 | Dark Theme QA | — | Contrast + token audit |
| 19 | Accessibility Review | — | Focus order, SR labels, AA, reduced-motion |
| 20 | Interaction Specs | — | This document + motion notes |

Frames 1, 4, 13 are rendered; the rest are specced here and rendered the same way (HTML → PNG)
as each is implemented.

## Premium interactions ("wow" moments)

- **Live AI timeline** — not "Generating…" but: ✓ Building context → ✓ Selecting prompt →
  ✓ Calling Claude → ✓ Drafting → ✓ Formatting → ✓ Version saved. The running step glows cyan.
- **Live token meter** — `1,231 tokens · $0.0142`, ticking up during generation (mono, tabular).
- **AI provenance** — model · prompt version · generated-at · duration · cost on every artifact.
- **Version timeline** — `v4 Human · v3 Claude · v2 Human · v1 Claude` communicates history at a glance.
- **Split view** — Markdown ⇄ Preview ⇄ Diff, instant switch.

## Expanded component library

Reusable across the product (extends [07 — Component Library](07-component-library.md)):

`CommandPalette` · `AIStatusBar` · `ArtifactCard` · `VersionTimeline` · `CostBadge` ·
`PromptViewer` · `GenerationTimeline` · `WorkspaceTabs` · `MetadataInspector` · `ActivityFeed`.

## Signature-screen test

> If a screenshot of this workspace were posted without context, another engineer should
> recognize it as *this* product. Consistent tokens, the four-zone IA, cyan-for-AI, and the
> provenance/cost transparency are the signature.

## Implementation note

Build with shadcn/ui + Radix + Framer Motion against these mockups — no redesign, no
second-guessing. The HTML prototypes are the source of truth for spacing, type, and color.
