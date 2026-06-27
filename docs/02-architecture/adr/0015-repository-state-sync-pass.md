# 0015 — RepositoryState and the RepositorySyncPass

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0010](0010-build-planner-diff.md), [ADR-0012](0012-identity-federation-boundary.md), [ADR-0013](0013-typed-compiler-context.md), [ADR-0014](0014-compiler-fingerprint-and-dependency-graph.md)

## Context

The compiler knows everything about *local* artifacts — it builds them, hashes them, explains them.
It knew nothing about what the *remote* holds. Publishing was fire-and-forget: no way to ask "is the
remote in sync, and what's pending?" The build-planner/diff work (ADR-0010) anticipated this and
named it: treat GitHub as *synchronization*, not re-upload.

This was also the test the architecture had been building toward: could a genuinely new capability
arrive as **pure addition** — one `ContextKey`, one pass, one report section — touching no existing
pass?

## Decision

**`RepositoryState` — the remote analogue of `CompilationReport`.** A versioned domain model
describing *the state of publication*, independent of transport: `repository`, `default_branch`,
`published_commit`, `remote_artifact_hashes`, `sync_status`, `pending_artifacts`, `last_sync`,
`remote_fingerprint`, `diagnostics`. It is not a GitHub response wrapper — GitHub is one
implementation; nothing in the model names it. `build_repository_state` is a pure comparison of
local hashes against a remote snapshot, fully testable without a network.

**`RepositorySyncPass` — observe, don't decide.** One new pass: `consumes=(BUNDLE,)`,
`produces=(REPOSITORY_STATE,)`. It reads the remote via a read-only `RepositoryReader` port and
produces the comparison. It is the **one pass that is neither `deterministic` nor `cacheable`** —
the remote can change between runs, so the flags finally diverge from the all-pure extraction passes,
exactly as the `cacheable`/`deterministic` split (ADR-0011) anticipated.

**Responsibilities stay separated.** The planner still decides *what* to build; the publisher still
decides *how* to transmit; the sync pass answers only *"what does the remote look like now?"* It
makes no publishing decision.

**The credential is configuration, not a slot.** The reader carries the token, injected at the
boundary (`get_repository_reader`). So a credential never enters the typed symbol table — which is
also what keeps secrets out of the input hashes and fingerprint. The compiler still never sees
identity; it sees a reader.

**One new report section.** When a `RepositoryState` is present, the `CompilationReport` surfaces the
`published_commit` and `sync_status` (the `commit_sha` / `publisher_result` fields reserved in
ADR-0013). Pure enrichment — no pass changed.

## Alternatives considered

- **Make `RepositoryState` a GitHub API response object.** Rejected: it would leak the transport into
  the model and block a second publisher. The state is about *publication*, not about GitHub.
- **Let `RepositorySyncPass` publish when out of sync.** Rejected: that collapses observe/decide/transmit
  into one pass and breaks the boundaries the project has held. Sync observes; publishing stays separate.
- **Put the credential and repository id in the context as slots.** Rejected: secrets would be hashed
  into `input_hash`/fingerprint. Reader-as-configuration keeps them out.

## Trade-offs

- (+) GitHub becomes synchronization: the system can state what's published and what's pending.
- (+) Delivered as pure addition — one key, one pass, one report section; every existing pass byte-for-byte
  unchanged (the explain fingerprint is identical before and after).
- (+) Transport-independent state model; a second publisher is a new reader, not a model change.
- (−) `last_sync` and `remote_fingerprint` are present but unfilled until sync history is persisted and
  the remote exposes a manifest — honest placeholders, not dead fields.
- (−) The real GitHub reader recomputes content hashes from blobs (N requests); fine at these sizes,
  and a committed manifest can short-circuit it later.

## Consequences

- `GET /projects/{id}/repository-state?repository=…` reports `in_sync` / `ahead` / `unpublished` with
  the pending set. `RepositoryState` joins the typed outputs as another `ContextKey`.
- Publishers can later consume the pending set to push only what changed — true incremental publish.

## Future revisit

Persist sync history (fills `last_sync`); have the publisher write and the reader read a manifest of
our content hashes + compiler fingerprint (fills `remote_fingerprint`, avoids per-blob fetches); and
let the publisher consume `pending_artifacts` to transmit only the diff.
