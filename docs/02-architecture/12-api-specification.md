# 12 — API Specification

The API is derived from **resources**, not invented endpoint-by-endpoint. We name the nouns
first, then expose standard operations on them. This yields a smaller, more consistent surface.

## Resources

`Users` · `Workspaces` · `Projects` · `Artifacts` · `Prompts` · `Runs` (generations) ·
`Repositories` · `Releases` · `Templates` · `Providers`

## Conventions

- **Base:** `/api/v1`. Versioned in the path; breaking changes bump the version.
- **Auth:** HTTP-only session cookie (ADR-0003); CSRF token on mutations.
- **Format:** JSON. Resource ids are UUIDs.
- **Errors:** RFC 7807 `application/problem+json`:
  ```json
  { "type": "about:blank", "title": "Validation failed", "status": 422,
    "detail": "idea must not be empty", "instance": "/api/v1/projects" }
  ```
- **Pagination:** cursor-based — `?limit=20&cursor=...` → `{ "data": [...], "next_cursor": "..." }`.
- **Idempotency:** unsafe POSTs that create external effects (repo export, generation) accept an
  `Idempotency-Key` header.
- **Streaming:** generation responses stream via **SSE** (`text/event-stream`).

## Endpoints derived from resources

### Projects
| Method | Path | Purpose |
|---|---|---|
| GET | `/projects` | List the workspace's projects |
| POST | `/projects` | Create from `{ title, idea }` |
| GET | `/projects/{id}` | Fetch a project + lifecycle stage |
| PATCH | `/projects/{id}` | Update title/idea/stage |
| DELETE | `/projects/{id}` | Delete (cascades artifacts) |

### Artifacts (nested under a project)
| Method | Path | Purpose |
|---|---|---|
| GET | `/projects/{id}/artifacts` | List artifacts |
| GET | `/projects/{id}/artifacts/{aid}` | Fetch current version |
| PUT | `/projects/{id}/artifacts/{aid}` | Save a human edit → new version |
| GET | `/projects/{id}/artifacts/{aid}/versions` | Version history |

### Runs (generations)
| Method | Path | Purpose |
|---|---|---|
| POST | `/projects/{id}/runs` | Start a generation `{ artifact_type, provider_id, model }` → **SSE stream** |
| GET | `/projects/{id}/runs` | List runs (cost/latency history) |
| GET | `/runs/{rid}` | Fetch a run record (tokens, cost, latency, status) |

### Repositories & Releases
| Method | Path | Purpose |
|---|---|---|
| POST | `/projects/{id}/repository` | Scaffold + create GitHub repo (idempotent) |
| GET | `/projects/{id}/repository` | Linked repo info |
| POST | `/projects/{id}/repository/releases` | Create a release/tag |

### Providers, Templates, Workspaces, Users
| Method | Path | Purpose |
|---|---|---|
| GET/POST/DELETE | `/providers` | List/connect/disconnect AI providers |
| GET/POST | `/templates` | List/create reusable templates |
| GET | `/workspaces/current` | Current workspace |
| GET | `/users/me` | Current user |
| POST | `/auth/login`, `/auth/logout`, `/auth/github` | Session lifecycle (ADR-0003) |

## Example — start a generation (SSE)

```
POST /api/v1/projects/{id}/runs
{ "artifact_type": "prd", "provider_id": "…", "model": "…" }

→ 200 text/event-stream
event: token   data: {"text":"## Overview"}
event: token   data: {"text":" Engineering OS …"}
event: done    data: {"run_id":"…","version_id":"…","tokens_out":1240,"cost_cents":3,"latency_ms":4200}
```

The `done` event returns the persisted `version_id` (Principle 3: the output is a versioned
artifact, not a transient message) and the run's cost/latency (Principle 4).

## Why resources-first

Every resource gets the same predictable verbs, so the surface stays small and learnable;
new capabilities usually mean a new resource, not a bespoke endpoint. Mobile and plugin clients
consume the exact same API — no parallel surface to maintain.
