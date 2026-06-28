# 22 — Architecture diagrams

Rendered inline by GitHub (Mermaid). They summarize the model specified in
[20 — Compiler specification](20-compiler-specification.md).

## The compilation pipeline

How a project becomes published artifacts — knowledge → plan → execute → identity → sync.

```mermaid
flowchart TD
  P[Project: title · idea · sources] --> K[KnowledgeGraph]
  K --> D[DecisionGraph]
  K --> B[ArtifactBundle]
  D --> X[ExplanationGraph]
  B --> X
  subgraph plan_exec [plan → execute only the minimal subgraph]
    PLAN[ExecutionPlan · predictive] --> EXEC[Dependency executor · sequential]
  end
  K & D & B & X --> PLAN
  EXEC --> REP[CompilationReport · historical]
  EXEC --> BUN[ArtifactBundle · hashed]
  REP --> MAN[BuildManifest · immutable identity]
  BUN --> MAN
  BUN --> SYNC[RepositorySyncPass]
  SYNC --> RS[RepositoryState · the outside world]
```

Everything above `RepositoryState` is a completed fact; `RepositoryState` is the one mutable
observation of the world.

## The application boundary

Identity wraps the compiler; the compiler never sees a user or a token.

```mermaid
flowchart LR
  U[Browser] -->|OAuth| AUTH[Identity · Authorization]
  AUTH -->|authorize project| COMP[Compiler · receives a Project]
  AUTH -->|credential via port| PUB[Publishers]
  COMP --> ART[ArtifactBundle]
  ART --> PUB
  PUB --> GH[(GitHub)]
  classDef core fill:#eef,stroke:#88a;
  class COMP,ART core;
```

## Request diagnostics

Every request is correlated; every failure is traceable.

```mermaid
flowchart LR
  REQ[HTTP request] --> MW[DiagnosticsMiddleware]
  MW -->|X-Request-ID · timing| RT[Route handler]
  MW -->|throughput · latency| MET[/metrics · Prometheus/]
  MW -->|one structured line| LOG[(access log)]
  RT -->|unhandled| EX[Exception handler]
  EX -->|trace_id in body + log| RESP[500 + trace_id]
  RT --> OK[2xx/4xx + X-Request-ID]
```

## Deployment topology

`docker compose up` — the API runs migrations, then serves; it waits for a healthy database.

```mermaid
flowchart LR
  subgraph stack [docker compose]
    API[API · uvicorn · prod profile]
    PG[(Postgres 16)]
    RX[(Redis 7)]
  end
  API -->|migrate then serve| PG
  API -.->|cache / rate-limit store| RX
  DEV[Engineer] -->|:8000 · /health/ready| API
  API -->|alembic upgrade head| PG
```
