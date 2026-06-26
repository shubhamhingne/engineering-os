# Initial Technology Stack

The concrete selections for the MVP. This refines [ADR-0002](../02-architecture/adr/0002-tech-stack.md)
with specific libraries. **Documented, not yet implemented.** Each entry notes *why* and what it
replaces if reconsidered.

## Frontend (`apps/web`, `packages/ui`)

| Choice | Role | Why |
|---|---|---|
| Next.js (App Router) | Framework | SSR + streaming for AI output; portfolio fit |
| React + TypeScript | UI + types | Strict typing; shared contracts |
| Tailwind CSS | Styling | Token-driven; maps 1:1 to the design system |
| shadcn/ui | Component base | Unstyled, accessible primitives we theme with our tokens — own the code, no lock-in |

## Backend (`apps/api`)

| Choice | Role | Why |
|---|---|---|
| FastAPI (Python 3.12) | API framework | Async-native, typed, ideal for AI workloads |
| SQLAlchemy 2.0 | ORM | Typed, explicit |
| Alembic | Migrations | Reversible, reviewed-as-code |
| Pydantic | Boundaries/validation | Request/response + settings |

## Database & cache

| Choice | Role | Why |
|---|---|---|
| PostgreSQL | Primary store | Relational integrity + JSONB for artifact content |
| Redis | Cache / queue / streaming | Generation buffers, job queue, rate limits |

## Authentication

| Choice | Role | Why |
|---|---|---|
| Better Auth (candidate) | Auth | Modern, self-hostable, no vendor lock-in; email + GitHub OAuth (see [ADR-0003](../02-architecture/adr/0003-authentication.md)) |

> Auth library is the least-locked decision: it sits behind our own session model, so swapping it
> is contained. Final choice confirmed at implementation.

## AI

| Choice | Role | Why |
|---|---|---|
| Provider abstraction (`AIProviderPort`) | Core | No vendor SDK in the domain (Principle 5) |
| OpenAI · Anthropic · Gemini adapters | Providers | Multi-model from day one; user-selectable |

## Infrastructure

| Choice | Role | Why |
|---|---|---|
| Docker / docker-compose | Local + reproducible builds | Same image local → prod |
| GitHub Actions | CI/CD | Inherits org standards; gates merges |
| Managed Postgres/Redis | Stateful services | No DB ops; backups/PITR |

## What is deliberately NOT chosen yet

State management library, specific hosting provider, and the Markdown editor library are left open
until implementation, because they're cheap to decide late and benefit from real usage signal.
Premature selection here would be guessing.
