# EDR-001 — Engineering Workspace component architecture

An Engineering Design Review is the gate **before** any implementation. It answers the hard
questions about reuse, state, scale, accessibility, and testability so the code is right the
first time. This EDR covers the workspace component library (Day 11).

## Decision summary

Build a **reusable, type-agnostic** workspace library: presentational components driven by
props, a single data hook for server state, primitives from the design system, and centralized
motion. The shell composes zones; zones compose components.

## EDR questions — answered

**Is each component reusable?**
Yes. Components are props-driven and **artifact-type-agnostic** — `ArtifactEditor`,
`MarkdownPreview`, `DiffViewer`, `VersionTimeline`, etc. take data, not a hardcoded "Vision".
The same components render Vision, PRD, README, ADR, and future types unchanged.

**Is there unnecessary state?**
No. **Server state** (project, artifacts, versions) lives in one hook, `useWorkspace`, which
owns fetching and mutations. **UI state** is local and minimal: active tab, view mode
(Markdown/Preview/Diff), selected version. No global store — it isn't needed yet; the hook is the
seam where one (or React Query) slots in later without touching presentation.

**Does this belong in the design system?**
Split by reuse scope: **primitives** (`Button`, `Badge`, `cn`) are design-system/`ui`, shareable
across the product; **workspace compositions** (`AIContextPanel`, `GenerationTimeline`) are a
feature library. This prevents the design system from absorbing product-specific concepts.

**Will this scale to 20 artifacts instead of 2?**
Yes — the tree and tabs are **data-driven** from the artifact set (ADR-0004). Adding a type is an
enum value + a prompt template; the UI renders it with zero new components. The editor never
knows the type.

**Can the animation be reused?**
Yes. Motion lives in `lib/motion.ts` as shared Framer variants (fade/rise, list stagger, the
generation-step reveal). Components reference variants, never bespoke inline animations —
consistent and reduced-motion-aware in one place.

**Does this meet accessibility requirements?**
Tabs use **Radix** (keyboard + ARIA for free); focus is managed on view changes; motion respects
`prefers-reduced-motion` via `useReducedMotion`; tokens meet WCAG AA; every icon-only control has
a label. A11y is in the components, not a later pass.

**Can this be tested in isolation?**
Yes. Presentational components are **pure** (props → UI) and unit-testable without a network. The
`useWorkspace` hook isolates I/O so it can be tested or mocked independently of rendering.

## Component responsibilities

| Component | Responsibility | Pure? |
|---|---|---|
| `WorkspaceShell` | Composes the four zones; owns layout | layout only |
| `ArtifactTree` | Lists typed artifacts + status | ✅ |
| `ArtifactTabs` | Radix tabs over artifact types | ✅ |
| `ArtifactEditor` | Edit/generate/save (uses hook callbacks) | mostly |
| `MarkdownPreview` | Render Markdown | ✅ |
| `DiffViewer` | Line diff between versions | ✅ |
| `VersionTimeline` | Version history visual | ✅ |
| `AIContextPanel` | Provider, meter, provenance, actions | ✅ |
| `GenerationTimeline` | Step progress during generation | ✅ |
| `TokenCostBadge` | Tokens + cost (mono, tabular) | ✅ |
| `MetadataInspector` | Provenance key/values | ✅ |
| `BottomActivityPanel` | Version timeline + activity feed | ✅ |
| `useWorkspace` (hook) | Server state + mutations | I/O seam |

## State architecture

```
useWorkspace(projectId)  ──▶  { project, artifacts, versions, generate(), save() , loading, error }
        │ (server state, the only I/O)
        ▼
WorkspaceShell  ──▶ zones ──▶ presentational components (local UI state only)
```

## Verdict

**EDR passed.** Proceed to implementation against the
[approved prototype](../03-design-system/18-workspace-design-spec.md). Build to production
quality — no temporary styling, no throwaway components.
