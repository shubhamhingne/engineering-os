# 06 — Roadmap

Three horizons. Each is shippable on its own and showcases a wider slice of the stack —
deliberately, so the portfolio value compounds with the product.

## MVP — "Idea to standards-compliant repo"

**Theme:** Prove the core loop end-to-end for a single user.

- Auth (email + GitHub OAuth)
- Project workspace (create, list, lifecycle stage)
- AI generation order (revised): **Vision → PRD → Repository Bootstrap → README → ADR**
  (editable, versioned). Bootstrapping the repo *before* the README/ADR gives the user something
  tangible early, and lets ADRs be generated with real repository context — making them more
  grounded.
- Multi-model support (provider abstraction, model selector)
- GitHub scaffolding (create repo + push standards + docs)
- PostgreSQL persistence; structured logging
- **Shipped (Day 9):** Vision slice — create project → generate Vision → edit → save → reopen,
  with tests and observability.
- **Shipped (Day 10):** Artifact abstraction (typed `Artifact` + version history, ADR-0004) and
  PRD generation from the Vision; tabbed UI (Vision · PRD · Activity); 14 tests passing.
- **Shipped (Day 10.5–11):** signature four-zone Engineering Workspace (designed, then implemented
  as a 12-component library on one I/O hook).
- **Shipped (Day 12):** streaming generation (SSE, ADR-0005) — live stages + growing content,
  functional command palette (⌘K), version diff, premium empty states; 16 tests passing.
- **Shipped (Day 13):** Project Export Pipeline (`ExportJob`, ADR-0006) — streamed phases
  (queued→preparing→generating→packaging→verifying→done), real downloadable ZIP, export history +
  download center, dedicated export panel; 19 tests passing.

**Stack showcased:** Next.js (web) · FastAPI (Python) · PostgreSQL · Auth · LLM integration ·
GitHub API · Docker · CI/CD.

**Definition of done:** a user goes from idea to a pushed, standards-compliant repo in one
session; all artifacts persist.

## v2 — "From documents to a guided workflow"

**Theme:** Make the lifecycle active and reachable beyond the desktop.

- Lifecycle tracker with per-stage status and checklists
- ADR management (supersede, index) and project knowledge base
- **Agentic workflows** — multi-step agents that complete a stage with human checkpoints (MCP/tool use)
- Documentation generation from artifacts
- **Mobile companion** (Flutter or Android) — review and approve artifacts on the go
- WebSocket streaming for live generation

**Stack showcased (adds):** Agentic AI / MCP · WebSockets · Flutter/Android · background jobs.

## v3 — "Teams and ecosystem"

**Theme:** Multiply value across people and projects.

- Shared workspaces, roles, and review flows
- Code-review assistant (diff vs. standards)
- Template/blueprint library and marketplace
- Analytics on lifecycle health across a portfolio
- Self-host / bring-your-own-keys option

**Stack showcased (adds):** multi-tenant architecture · RBAC · billing · React Native (cross-platform) · infra automation.

## Releases

Tracked as releases, not days — a real product roadmap.

| Release | Theme | Status |
|---|---|---|
| Alpha-0.3 | Core engine (workspace · streaming · export) | ✅ shipped |
| Alpha-0.4 | README synthesis (KnowledgeGraph, ADR-0007) | ✅ shipped |
| Alpha-0.5 | ADR generation (DecisionGraph, ADR-0008) | ✅ shipped |
| Alpha-0.6 | Semantic build system + GitHub publisher (ADR-0009) | ✅ shipped |
| Alpha-0.6.x | Incremental build pipeline — planner · hashing · diff (ADR-0010) | ✅ shipped |
| Alpha-0.7 | Explainability — `ExplanationGraph` + `CompilerPass` pipeline (ADR-0011) | ✅ shipped |
| Alpha-0.8 | Identity · Authorization · Federation — GitHub OAuth (ADR-0012) | ✅ shipped |
| Alpha-0.8.x | Typed `CompilerContext` — symbol table · startup validator · build log (ADR-0013) | ✅ shipped |
| Alpha-0.8.y | Compiler self-knowledge — fingerprint · pass versions · dependency graph (ADR-0014) | ✅ shipped |
| Alpha-0.9 | Repository synchronization — `RepositorySyncPass` + `RepositoryState` (ADR-0015) | ✅ shipped |
| v1.0-α1 | Pass-output caching — activates `cache_hit` · `artifacts_reused` (ADR-0016) | ✅ shipped |
| v1.0-α2 | Dependency-driven execution — `ExecutionPlan` · minimal subgraph (ADR-0017) | ✅ shipped |
| v1.0-α3 | `BuildManifest` — immutable, content-addressed compilation identity (ADR-0018) | ✅ shipped |
| v1.0-α4 | Compiler hardening — property-based invariant testing, Hypothesis (ADR-0019) | ✅ shipped |
| v1.0-α5 | Compiler guide — one teachable document of the whole model | next |
| v1.0-α6 | AI-backed pass implementations — behind `CompilerPass`, deterministic fallback | planned |
| v1.0-α7 | Compiler replay — reconstruct execution from the manifest | planned |
| v1.0 | Public launch | planned |

## Sequencing principle

Each horizon is a complete, demonstrable product — never a half-built bridge to the next.
The MVP alone is interview-worthy; v2 and v3 deepen the story and broaden the stack on display.
