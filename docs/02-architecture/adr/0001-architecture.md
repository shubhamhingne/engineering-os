# 0001 — Architecture style: modular monolith with hexagonal core

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [08 — System Architecture](../08-system-architecture.md), ADR-0002

## Context

Engineering OS is built and operated by a single engineer at MVP stage, but must remain
modular and provider-agnostic (Principles 1–5) and must evolve toward mobile clients, plugins,
and team workspaces. We need an architecture that is cheap to operate now and does not have to
be torn down later.

## Decision

Build a **modular monolith**: one deployable backend (FastAPI) and one frontend (Next.js).
Internally, the backend uses **hexagonal architecture (ports & adapters)** — an application
core of cohesive modules (Projects, Artifacts, Generation, Repo Export) that reach all
external systems (AI providers, GitHub, persistence) through ports with swappable adapters.

## Alternatives considered

- **Microservices.** Strong isolation and independent scaling. Rejected for the MVP:
  operational overhead (deploys, networking, distributed debugging) is unjustified for one
  developer and modest load; premature decomposition would slow delivery.
- **Serverless functions.** Cheap idle cost, easy scaling. Rejected as the primary style:
  long, streaming AI generations and stateful jobs fit poorly with function timeouts and cold
  starts; harder to keep a clean domain core.
- **Unstructured monolith (no ports).** Fastest to start. Rejected: would violate Principle 5
  (replaceable providers) and make the AI/GitHub integrations hard to test and swap.

## Trade-offs

- (+) Low operational cost; simple local dev; one deploy.
- (+) Clean seams (ports) preserve modularity and testability.
- (−) Everything scales together; a hot path can't scale independently yet.
- (−) Hexagonal structure is more upfront ceremony than a flat app.

## Consequences

- Modules communicate through interfaces, not direct imports across boundaries.
- External calls (AI, GitHub, DB) are always behind a port — enabling fakes in tests.
- A module can later be extracted into its own service with minimal churn because its
  boundary already exists.

## Future revisit criteria

Revisit if **any** holds: sustained load requires independent scaling of the generation path;
the team grows beyond ~3 engineers wanting independent deploy cadences; or a single module's
resource profile (e.g. heavy async generation) destabilizes the rest. First step would be to
extract the **Generation/worker** path into its own service — the port boundary makes this low-risk.
