# 02 — Product Requirements Document

## Overview

Engineering OS is a web application where a developer creates a **project**, moves it through
the engineering lifecycle with AI assistance, and exports a **scaffolded GitHub repository**
that already meets opinionated engineering standards.

The MVP delivers one complete loop and nothing more:

> **Idea → AI-generated lifecycle artifacts (Vision, PRD, ADRs, README) → a GitHub repo
> scaffolded from the `.github` standards.**

## Goals

- Take a one-paragraph idea to a documented, standards-compliant repository in under an hour.
- Make the *thinking* artifacts (Vision, PRD, ADRs) first-class and editable, not throwaway
  chat output.
- Apply consistent engineering standards automatically via GitHub integration.

## Non-goals (MVP)

- Not an IDE or code-completion tool — it does not write the application's feature code.
- Not a project-management replacement (no sprints, boards, time tracking) in the MVP.
- Not real-time multiplayer; single-user workspaces only at first.
- Not mobile in the MVP (web only).

## Target users (summary)

Solo developers and senior engineers building a credible portfolio, indie hackers shipping
side projects, and small teams without dedicated PM/architect roles. Full detail in
[04 — Personas](04-personas.md).

## Feature prioritization (MoSCoW)

### Must have — the MVP
- **Authentication** — email/password and **GitHub OAuth**.
- **Project workspace** — create, name, and describe a project; list projects.
- **AI artifact generation** — guided, editable generation of: Product Vision, PRD,
  Architecture overview + ADRs, and a README.
- **Editable artifacts** — every generated doc is Markdown the user can edit and version.
- **Multi-model support** — provider abstraction with at least two models selectable per
  generation (e.g. a frontier model and a fast/cheap model).
- **GitHub scaffolding** — one action creates a repo and pushes a standards-compliant
  scaffold (README, LICENSE, `.github` config, docs/ artifacts) using the `.github` repo.
- **Persistence** — projects and artifacts stored durably (PostgreSQL).

### Should have — fast-follow
- **ADR management** — list, supersede, and index ADRs.
- **Lifecycle tracker** — checklist of the 9 stages with status per project.
- **Documentation generation** — derive README/usage docs from existing artifacts.
- **Project knowledge base** — store decisions/notes the AI can reference within a project.

### Could have — later
- **Code review assistant** — review a diff against the standards.
- **Agentic workflows** — multi-step agents that complete a whole stage with checkpoints.
- **Template library** — reusable project blueprints.

### Won't have (this cycle)
- Mobile apps, real-time collaboration, self-hosting, team billing/roles.

## Functional requirements (MVP)

| ID | Requirement |
|---|---|
| FR-1 | Users can sign up / sign in with email or GitHub OAuth. |
| FR-2 | Users can create a project with a title and a free-text idea description. |
| FR-3 | The system generates a Product Vision artifact from the idea; the user can edit and save it. |
| FR-4 | The system generates a PRD from the vision; editable and versioned. |
| FR-5 | The system generates an Architecture overview and at least one ADR; editable. |
| FR-6 | The system generates a README from the artifacts. |
| FR-7 | Users can select the model used for any generation. |
| FR-8 | Users can connect GitHub and create a new repository from a project. |
| FR-9 | On export, the repo is scaffolded with the `.github` standards and the project's `docs/` artifacts, then pushed. |
| FR-10 | All artifacts persist and reload across sessions. |

## Non-functional requirements

- **Security:** OAuth tokens encrypted at rest; no secrets in logs; least-privilege GitHub scopes.
- **Reliability:** generation failures are recoverable; partial work is never lost.
- **Performance:** artifact generation streams; first token < 3s under normal load.
- **Cost control:** per-generation token budgets; model choice exposes the cost/speed tradeoff.
- **Observability:** structured logs and basic usage metrics from day one.

## Assumptions

- Users have (or will create) a GitHub account and will grant repo-scoped access.
- LLM provider APIs are available and within budget for the expected volume.
- The opinionated `.github` standards are acceptable defaults for most users (overridable later).

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Scope creep ("AI workspace" wants every feature) | High | Hard MVP boundary; MoSCoW enforced; v2 backlog parked |
| Generic AI output that reads like a template | High | Strong prompts, the user as editor-in-chief, critique passes |
| LLM cost per active user | Medium | Token budgets, model tiering, caching, cheap-model defaults |
| GitHub API/token complexity | Medium | Start with a minimal scope; isolate integration behind one service |
| "Just another AI tool" perception | Medium | Lead with the lifecycle and standards, not the chatbox |
| Single-developer delivery risk | Medium | MVP scoped to be buildable solo; defer everything non-essential |
