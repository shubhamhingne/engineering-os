# 11 — Database Design

PostgreSQL. Relational integrity for the domain, JSONB for flexible artifact content and
provider/model options. Append-only versioning preserves history (Principle 3).

## Entity-relationship diagram

```mermaid
erDiagram
    users ||--|| workspaces : owns
    workspaces ||--o{ projects : contains
    workspaces ||--o{ templates : has
    workspaces ||--o{ providers : configures
    projects ||--o{ artifacts : has
    artifacts ||--o{ artifact_versions : has
    artifacts }o--|| artifact_versions : current
    generation_runs ||--o| artifact_versions : produces
    generation_runs }o--|| prompt_versions : uses
    generation_runs }o--|| providers : via
    projects ||--o| repositories : exports_to
    repositories ||--o{ releases : tags

    users { uuid id PK; citext email UK; text name; text password_hash; timestamptz created_at }
    workspaces { uuid id PK; uuid owner_id FK; text name; timestamptz created_at }
    projects { uuid id PK; uuid workspace_id FK; text title; text idea; text lifecycle_stage; timestamptz created_at; timestamptz updated_at }
    artifacts { uuid id PK; uuid project_id FK; text type; text title; uuid current_version_id FK; timestamptz created_at }
    artifact_versions { uuid id PK; uuid artifact_id FK; text content; text source; int version_no; timestamptz created_at }
    prompt_versions { uuid id PK; text artifact_type; int version; text body; bool active }
    providers { uuid id PK; uuid workspace_id FK; text vendor; jsonb model_options; bytea credential_enc; timestamptz created_at }
    generation_runs { uuid id PK; uuid project_id FK; uuid artifact_id FK; uuid produced_version_id FK; uuid prompt_version_id FK; uuid provider_id FK; text model; text status; int tokens_in; int tokens_out; int cost_cents; int latency_ms; jsonb params; text error; timestamptz created_at }
    repositories { uuid id PK; uuid project_id FK UK; text github_full_name; text default_branch; timestamptz created_at }
    releases { uuid id PK; uuid repository_id FK; text version; text tag; text notes; timestamptz created_at }
    templates { uuid id PK; uuid workspace_id FK; text scope; text body; timestamptz created_at }
```

## Design decisions

- **UUID primary keys** (v7/time-ordered) — safe to expose, index-friendly, no enumeration.
- **Append-only `artifact_versions`** — immutable history; `artifacts.current_version_id`
  points at the active revision. "Edit" = insert a new version, never update content.
- **`source` on each version** (`ai` | `human` | `import`) — provenance for Principle 1.
- **`generation_runs` is the observability spine** — every run (success or failure) records
  prompt version, provider, model, tokens, cost, latency, params (Principles 2 & 4). It is
  append-only and never updated after completion.
- **JSONB only where structure is genuinely open** — `provider.model_options`,
  `generation_runs.params`. Core relationships stay relational.
- **Secrets as `bytea` (`credential_enc`)** — provider credentials are envelope-encrypted at
  the application layer; the DB never sees plaintext ([16](16-security-model.md)).

## Indexing

| Table | Index | Reason |
|---|---|---|
| projects | (workspace_id, updated_at desc) | List a user's projects, recent first |
| artifacts | (project_id, type) | Fetch a project's artifact by type |
| artifact_versions | (artifact_id, version_no desc) | Latest/version history |
| generation_runs | (project_id, created_at desc) | Run history, cost/latency reporting |
| generation_runs | (provider_id, created_at) | Per-provider cost rollups |
| providers | (workspace_id, vendor) | Resolve a workspace's provider |

## Integrity & lifecycle

- FKs with `ON DELETE CASCADE` from project → artifacts → versions; `repositories` link is
  `SET NULL`/removed on project delete (never deletes the GitHub repo).
- `repositories.project_id` is **unique** (one repo per project in MVP).
- Check constraint: `artifacts.current_version_id` must belong to the same artifact (enforced
  in application + a deferred trigger).

## Migrations

Alembic, one migration per change, reviewed like code. Migrations must be **reversible** and are
gated in CI. No manual schema edits.
