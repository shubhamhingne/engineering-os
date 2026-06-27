# 0006 — Export as an observable pipeline (ExportJob)

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0004](0004-artifact-abstraction.md), [ADR-0005](0005-streaming-generation.md)

## Context

The project needs to leave Engineering OS as a real, usable repository. The first instinct —
"generate a repository" as a single `POST /export` returning a file — is too small: export will
grow (GitHub push, multiple output formats, IDE handoff), and a one-shot call has no progress, no
history, and no observability.

## Decision

Model export as an **`ExportJob`** run through an **observable pipeline** that mirrors AI
generation: streamed phases over SSE, a persisted job record, and downloadable outputs.

```
queued → preparing → generating → packaging → verifying → done
```

The pipeline assembles a ZIP (README generated from the artifacts, LICENSE, `.gitignore`, and each
artifact under `docs/`), persists an `ExportJob` (status, filename, size, artifact count, bytes),
and exposes history + download endpoints. Progress **reuses the streaming infrastructure from
ADR-0005** — no new mechanism.

## Alternatives considered

- **`RepositoryGenerator` + one `POST /export`.** Simplest. Rejected: no progress, no history, and
  the name boxes us into "a repo" when the pipeline will produce many outputs.
- **Background worker + polling for status.** Robust at scale. Deferred: streaming gives live
  progress now without the worker; the job model is already the seam to add a queue later.
- **Build the ZIP on the client.** Avoids server storage. Rejected: the server owns the artifacts
  and the standards; packaging belongs there, and GitHub push (later) must be server-side.

## Trade-offs

- (+) Export is observable (phases, history) and consistent with generation — one mental model.
- (+) `ExportJob` is a growable seam: GitHub push and new outputs are new phases/fields, not a redesign.
- (+) Real, downloadable artifact today (tested ZIP), not a stub.
- (−) Storing ZIP bytes in the DB is fine at MVP scale but will move to object storage as exports grow.
- (−) README here is templated; AI README generation (Day 14) replaces it without changing the pipeline.

## Consequences

- Outputs are extensible (Download ZIP now; GitHub / VS Code / Cursor later) without domain change.
- Export history builds user trust — every export stays visible and re-downloadable.
- Observability: `export.completed` logs artifact count, size, and latency.

## Future revisit

Move ZIP storage to object storage and add a background queue when export volume or size warrants;
add GitHub push as a pipeline phase (Day 17).
