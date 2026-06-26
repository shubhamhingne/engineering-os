# 07 — Component Library

The product's vocabulary. Every screen is assembled from these; new components are added only
when an existing one genuinely can't serve. Each entry lists variants and the states every
interactive component must implement.

## Universal interactive states

Every interactive component must define: **default · hover · active · focus-visible · disabled ·
loading**. Focus-visible always uses `--focus-ring` (cyan, 2px). No component ships without all six.

## Foundation

| Component | Variants | Notes |
|---|---|---|
| **Button** | primary (`--action`), secondary (outline), ghost, danger, icon-only | sizes sm/md; loading shows spinner, preserves width |
| **Input** | text, with-prefix/suffix, invalid | inline error text below; 36px height (md) |
| **Select** | single, searchable | keyboard navigable; uses overlay surface |
| **Textarea** | auto-grow, fixed | used for short idea input |
| **Checkbox** | default, indeterminate | 16px target visual, 24px hit area |
| **Switch** | on/off | for binary settings (e.g. density) |
| **Tabs** | underline, segmented | keyboard arrow navigation |
| **Badge** | neutral, accent (AI), semantic | for artifact type, status, "AI" |
| **Tooltip** | — | required on all icon-only controls |
| **Toast** | info/success/warning/danger | non-blocking, auto-dismiss, stacked |
| **Modal / Dialog** | standard, destructive-confirm | focus-trapped; Esc to close |

## Navigation

| Component | Purpose |
|---|---|
| **Sidebar** | Primary nav; project tree; collapsible to icon-rail |
| **Breadcrumb** | Location within workspace → project → artifact |
| **Command Palette** | `⌘K` — search and run any action (Principle 4) |
| **Workspace Switcher** | Switch workspace (one in MVP; built for many) |
| **Project Selector** | Quick-jump between projects |

## AI

| Component | Purpose |
|---|---|
| **Prompt Editor** | View/edit the prompt; shows prompt version (Principle 3) |
| **Generation Timeline** | Streaming progress + step history of a run |
| **Provider Selector** | Choose provider/model per generation; shows cost tier |
| **Token Usage** | Live tokens + cost + latency (mono, tabular nums) |
| **Artifact Preview** | Rendered Markdown of the generated artifact |
| **Diff Viewer** | Compare artifact versions (human vs. AI edits) |

> AI components are the cyan-accented surfaces — color signals "this is the machine," and each
> exposes its provenance by default.

## Documentation

| Component | Purpose |
|---|---|
| **Markdown Editor** | Edit artifacts (16px reading scale); split or preview |
| **ADR Card** | Summarizes an ADR (status, date, title) in lists |
| **PRD Card** | Summarizes the PRD; links into sections |
| **Repository Card** | Linked GitHub repo: name, branch, last export |
| **Architecture Viewer** | Renders Mermaid diagrams from artifact content |

## Composition rules

- Components reference **tokens only** ([02](02-design-tokens.md)); no hard-coded values.
- Prefer composition over new variants — a "card with an AI badge" is `Card` + `Badge`, not a
  new component.
- Every component is documented with its props contract when implemented (Day 8+), but the
  vocabulary is fixed here so screens can be designed against it.

## Why fix the vocabulary first

Designing screens before components guarantees rework: the third screen invents a button the
first two didn't have. Naming the vocabulary up front means every wireframe ([14](14-wireframes.md))
is assembled from known parts, and implementation is composition, not invention.
