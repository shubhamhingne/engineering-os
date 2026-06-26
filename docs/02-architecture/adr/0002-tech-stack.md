# 0002 — Technology stack

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** ADR-0001

## Context

The stack must deliver a streaming AI web product, be productive for a solo builder, and
showcase the portfolio's target competencies (Next.js, FastAPI, Python, PostgreSQL, AI). It
must support server-sent streaming, async jobs, and clean provider abstraction.

## Decision

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Next.js (App Router) + TypeScript + Tailwind** | SSR, streaming UI, strong DX, portfolio fit |
| Backend | **FastAPI (Python 3.12)** | Async-native, typed, excellent for AI/LLM workloads |
| Data | **PostgreSQL** | Relational integrity + JSONB for artifact content/versions |
| Cache/queue | **Redis** | Streaming buffers, job queue, rate limiting |
| ORM/migrations | **SQLAlchemy 2.0 + Alembic** | Mature, typed, explicit migrations |
| AI access | **Provider port + per-provider adapters** | Principle 5; no SDK lock-in in the core |
| Auth | **GitHub OAuth + email/password** | See ADR-0003 |
| Infra | **Docker**, managed Postgres/Redis, CI via GitHub Actions | Reproducible, standards-aligned |

## Alternatives considered

- **Node/NestJS backend.** One language across the stack. Rejected: Python is the stronger AI
  ecosystem and a deliberate portfolio signal; FastAPI's async + typing fit the workload.
- **Django.** Batteries included. Rejected: heavier than needed; async story and API-first fit
  are weaker than FastAPI for a streaming AI service.
- **A single LLM SDK (e.g. one provider's SDK) in the core.** Faster to start. Rejected:
  violates Principle 5; the adapter layer is the whole point.
- **NoSQL (Mongo) primary store.** Flexible documents. Rejected: artifacts have real relational
  structure (versions, runs, repos); Postgres + JSONB gives both integrity and flexibility.

## Trade-offs

- (+) Two languages (TS + Python) — both are portfolio-relevant and well-suited to their layer.
- (+) Postgres + JSONB avoids a second datastore while keeping artifact content flexible.
- (−) Two runtimes to operate vs. a single-language stack.
- (−) Provider adapters add code the core must maintain.

## Consequences

- The core depends on a `ProviderPort` interface, never a vendor SDK directly.
- Streaming uses SSE from FastAPI to Next.js; Redis backs buffering and rate limits.
- Migrations are explicit (Alembic) and reviewed like code.

## Future revisit criteria

Revisit the data layer if artifact/version volume or query patterns outgrow Postgres+JSONB
(unlikely near-term). Revisit the language split only if team composition makes a single
language materially more productive than the portfolio and workload benefits of Python for AI.
