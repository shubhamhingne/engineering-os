# 13 — Folder Structure

A **monorepo** with two apps (`web`, `api`) and shared tooling. The backend's layout makes the
hexagonal boundaries (ADR-0001) physical: domain at the center, adapters at the edge.

## Top level

```
engineering-os/
├── apps/
│   ├── web/                # Next.js frontend
│   └── api/                # FastAPI backend
├── packages/
│   └── shared-types/       # OpenAPI-generated TS types shared by web
├── docs/                   # product + architecture docs (this set)
├── .github/                # CI, dependabot, etc. (bootstrapped from standards)
├── docker-compose.yml      # local: api + postgres + redis
└── README.md
```

> Monorepo over polyrepo: one product, tightly coupled web↔api contract, shared types, and a
> single CI. It also keeps the artifact docs beside the code that implements them.

## Backend — `apps/api` (hexagonal, feature-first)

```
api/src/engineering_os/
├── main.py                 # app wiring, dependency injection
├── config.py               # settings (env-driven)
├── interface/              # ── inbound adapters ──
│   ├── http/               # FastAPI routers, request/response schemas
│   └── sse/                # streaming endpoints
├── modules/                # ── application core (one folder per bounded context) ──
│   ├── projects/           # domain models, services, ports used
│   ├── artifacts/
│   ├── generation/         # orchestrates a run; depends on AIProviderPort
│   └── export/             # repo scaffolding; depends on GitHubPort
├── ports/                  # ── interfaces (the hexagon edges) ──
│   ├── ai_provider.py
│   ├── github.py
│   └── repository.py       # persistence port
├── adapters/               # ── outbound adapters (implement ports) ──
│   ├── ai/                 # openai.py, anthropic.py, gemini.py
│   ├── github/             # github_rest.py
│   └── db/                 # sqlalchemy models, repositories, alembic/
├── observability/          # logging, tracing, metrics (Principle 4)
└── tests/                  # unit (fakes for ports) + integration
```

**Rule:** `modules/` and `ports/` never import from `adapters/`. Dependencies point inward;
adapters depend on ports, not the reverse. This is what keeps providers replaceable.

## Frontend — `apps/web` (feature-first)

```
web/src/
├── app/                    # Next.js App Router (routes, layouts)
├── features/               # one folder per feature
│   ├── projects/           # components, hooks, api calls, types
│   ├── artifacts/          # editor, version history
│   ├── generation/         # model picker, streaming view
│   └── repository/         # export flow
├── components/ui/          # design-system primitives (Day 6)
├── lib/                    # api client, auth, sse client
└── styles/                 # tokens, globals
```

## Why this structure

- **Boundaries are physical** — you can see the hexagon in the tree; reviewers can enforce the
  dependency rule mechanically.
- **Feature-first on both sides** — work for a feature is co-located, not scattered by type.
- **Adapters are swappable** — adding a provider is a new file in `adapters/ai/`, registered
  against `ai_provider.py`. Nothing in `modules/` changes (Principle 5).
- **Evolves cleanly** — extracting the `generation` module to its own service later means
  lifting one folder plus its port, not untangling a ball of mud.
