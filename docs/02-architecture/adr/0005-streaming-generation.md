# 0005 — Streaming generation over SSE

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0004](0004-artifact-abstraction.md), [Sequence diagrams](../14-sequence-diagrams.md)

## Context

Generation was request/response: click → wait → result. Functional, but it feels static — the
product should feel *alive* (visible stages, content that grows as it's written). This requires
streaming from provider → backend → UI.

## Decision

Add a **Server-Sent Events** streaming endpoint
(`POST /projects/{id}/artifacts/{type}/stream`). The provider port gains
`stream(prompt) -> Iterator[str]`; the domain orchestrates a sequence of events:

```
stage(building_context) → stage(selecting_prompt) → stage(calling_model)
→ token … token (live)  → stage(formatting) → [persist version] → stage(saved) → done
```

The artifact version is persisted when the stream completes; the `done` event carries the
version number, model, token count, and latency. The non-streaming `generate` endpoint remains
for simple/programmatic use.

## Alternatives considered

- **WebSockets.** Bidirectional, heavier. Rejected: generation is one-way server→client; SSE is
  simpler, proxy-friendly, and sufficient.
- **Polling.** Trivial. Rejected: laggy and wasteful; can't stream tokens smoothly.
- **Keep request/response only.** Simplest. Rejected: it's the exact "feels like 2023" experience
  we're removing.

## Trade-offs

- (+) Live stages + growing content; the UI can show real progress and cost.
- (+) Provider stays behind the port — `stream` is just another method (Principle 5).
- (−) SSE over **POST** needs `fetch` + `ReadableStream` on the client (`EventSource` is GET-only).
- (−) Errors mid-stream need an in-band `error` event rather than an HTTP status.
- (−) Token/cost are approximate for the fake provider; exact usage comes from the real provider's
  final message.

## Consequences

- Every provider adapter implements `stream`; the fake streams deterministically, so the pipeline
  is **testable without a network** (2 streaming tests added).
- Observability is unchanged — `artifact.version.created` still fires on persistence.
- The frontend consumes the stream to drive the generation timeline and grow the editor live.

## Future revisit

Surface real per-run token/cost from the provider's final usage on the `done` event; add resumable
streams only if long generations and disconnects become a real problem.
