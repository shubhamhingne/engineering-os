# Workspace component library

The reusable foundation of Engineering OS — **one shell, many artifact capabilities**. Built to
the [approved prototype](../../../../../docs/03-design-system/18-workspace-design-spec.md) and
[EDR-001](../../../../../docs/08-decisions/edr-001-workspace.md). Every component is type-agnostic
(works for Vision, PRD, README, ADR, and future types unchanged) and composes design-system
primitives only.

## Architecture

```
useWorkspace(projectId)        // the only I/O — server state + mutations
   └─ WorkspaceShell           // composes the four zones (layout owner)
        ├─ ArtifactTree        // left: typed artifacts
        ├─ ArtifactTabs        // center: Markdown/Preview/Diff (Radix)
        ├─ ArtifactEditor      //         edit surface
        ├─ MarkdownPreview     //         render
        ├─ DiffViewer          //         draft vs. saved diff
        ├─ AIContextPanel      // right: provider · usage · provenance · generate
        │    ├─ TokenCostBadge
        │    ├─ MetadataInspector
        │    └─ GenerationTimeline
        └─ BottomActivityPanel // bottom: version timeline + activity
             └─ VersionTimeline
```

**Rule:** presentational components are pure (props → UI). All fetching/mutation lives in
`useWorkspace`. Local UI state (active tab, view mode, draft) stays in the shell.

## Usage

```tsx
import { WorkspaceShell } from "@/components/workspace/WorkspaceShell";

export default function ProjectPage({ projectId }: { projectId: string }) {
  return <WorkspaceShell projectId={projectId} />;
}
```

## Design-system compliance

- **shadcn-style primitives** (`ui/button`, `ui/badge`) + Tailwind **design tokens** (no inline styles).
- **Radix** (`@radix-ui/react-tabs`) for accessible view-mode tabs.
- **Framer Motion** only where it communicates state (content reveal, generation steps) — variants
  centralized in `lib/motion.ts`; reduced-motion honored globally in `globals.css`.
- **Lucide** icons.

## Scaling to 20 artifacts

Adding an artifact type is a config line in `ArtifactTree` + an enum/prompt on the backend
(ADR-0004). No component changes — the editor, preview, diff, versions, and AI panel are all
type-agnostic.

## Verification

Type-check and run on a machine with Node:

```bash
pnpm install
pnpm --filter web typecheck
pnpm --filter web dev   # http://localhost:3000  (API on :8000)
```
