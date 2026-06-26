# 06 — Roadmap

Three horizons. Each is shippable on its own and showcases a wider slice of the stack —
deliberately, so the portfolio value compounds with the product.

## MVP — "Idea to standards-compliant repo"

**Theme:** Prove the core loop end-to-end for a single user.

- Auth (email + GitHub OAuth)
- Project workspace (create, list, lifecycle stage)
- AI generation: Vision → PRD → Architecture + ADR → README (editable, versioned)
- Multi-model support (provider abstraction, model selector)
- GitHub scaffolding (create repo + push standards + docs)
- PostgreSQL persistence; structured logging

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

## Sequencing principle

Each horizon is a complete, demonstrable product — never a half-built bridge to the next.
The MVP alone is interview-worthy; v2 and v3 deepen the story and broaden the stack on display.
