# 0004 — Generalize VisionArtifact into a typed Artifact

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0001](0001-architecture.md), [Domain model](../10-domain-model.md), [Database](../11-database-design.md)

## Context

The first vertical slice (Day 9) shipped with a `VisionArtifact` — a single table holding one
row per project, with a version counter on the row. It proved the architecture, but it modelled
*Vision* specifically, not *artifacts* generally.

The product is fundamentally about **artifacts** (Vision, PRD, README, ADR) — that is the
positioning and the whole reason the domain was designed artifact-centric ([doc 10](../10-domain-model.md)).
Adding PRD against the Day-9 model would mean a new table, service, and endpoint *per type* —
duplication that grows linearly with every artifact type and diverges over time.

## Decision

Replace `VisionArtifact` with a generic, **typed `Artifact`** plus **append-only
`ArtifactVersion`** history and an `ArtifactType` enum (`VISION`, `PRD`, `README`, `ADR`):

- `Artifact(project_id, type)` — unique per (project, type).
- `ArtifactVersion(artifact_id, version_no, content, source, model)` — immutable; editing
  appends a new version (Principle 3).
- One `ArtifactService`, one generic endpoint set `/projects/{id}/artifacts/{type}` (+ `/versions`),
  and one `ArtifactEditor` component serve **every** type.
- Prompts live in the generation module keyed by type; the provider port just executes a prompt.

## Alternatives considered

- **Per-type tables/endpoints** (`VisionArtifact`, `PrdArtifact`, …). Rejected: O(types)
  duplication in schema, services, routes, and UI; logic diverges; contradicts the domain model.
- **One artifact row with a JSON blob of all types.** Rejected: loses per-type versioning and
  queryability; conflates distinct documents.
- **Event sourcing.** Rejected: overkill for the MVP. Append-only versions give the history we
  need with far less machinery.

## Trade-offs

- (+) Adding README/ADR later is **an enum value + a prompt template** — zero schema, endpoint,
  or UI churn.
- (+) Version history becomes first-class and uniform across all types.
- (+) The domain now matches the product: Project → Artifact(type) → Version.
- (−) A generic `/artifacts/{type}` route is slightly less self-documenting than `/vision`.
  Mitigated by a typed enum and an explicit 404 on unknown types.
- (−) One migration (VisionArtifact → Artifact/ArtifactVersion). Acceptable: no production data.

## Consequences

- PRD is generated from the project's current Vision; the prerequisite is enforced (409 if no
  Vision exists) — composition between artifacts is now a first-class concept.
- Observability became artifact-centric (`artifact.generated`, `artifact.version.created`).
- Future types (README in slice #3, ADR in slice #4) require no architectural change.

## Future revisit

If artifact types diverge enough to need type-specific fields, add per-type metadata (a JSONB
column on `Artifact`) rather than reintroducing per-type tables.
