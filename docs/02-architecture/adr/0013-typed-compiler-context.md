# 0013 — The typed CompilerContext: a symbol table, a validator, and a build log

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0011](0011-explainability-compiler-passes.md), [ADR-0010](0010-build-planner-diff.md)

## Context

ADR-0011 made every transformation a `CompilerPass` over a shared `dict[str, Any]` context, with
inputs validated **at runtime**. A dict scales surprisingly far, but it erases the one guarantee a
compiler should have: that the pipeline is *well-formed*. A pass that consumes a slot nothing
produces, two passes that produce the same slot, or a slot filled with the wrong type — none of
these are caught until the offending pass runs (or worse, until a later pass reads bad data).

The fix is not "replace `dict` with a typed object." It is to treat the context as the compiler's
**symbol table**, and to make the pass declarations rich enough to *prove* the pipeline correct
before any work runs.

## Decision

**Typed slot identifiers.** Each slot is a `ContextKey(name, type)` — module-level constants
(`KNOWLEDGE`, `DECISIONS`, `BUNDLE`, `EXPLANATIONS`, …). Passes consume and produce *keys*, not
strings, so validation is by identity and type, never string equality.

**`CompilerContext` — the symbol table.** Set/get slots by key; every write is type-checked, so a
pass cannot smuggle the wrong shape into a slot the next pass trusts. Alongside the semantic graphs
it carries compiler *metadata* (warnings, and — via the runner — an execution trace). The context
holds both the program's symbols and the facts about compiling it.

**`PassDescriptor`.** Every pass exposes `{id, consumes, produces, deterministic, cacheable}` as
data. The descriptor is the single source of truth for both the validator and (later) the scheduler.

**Startup validator.** `validate_pipeline` walks the passes once and proves: every consumed slot
has an earlier producer (or is seeded); a consumed slot's type matches how it is produced; no slot
has two producers. `Compiler.__init__` calls it, so an ill-formed pipeline **fails at construction**
— the explain pipeline is validated at import. (Cycle detection arrives with the DAG scheduler; a
linear list cannot cycle.)

**`CompilationReport` — the build log.** A run now yields not just outputs but a report:
`compiler_version`, `schema_versions` of every graph touched, a `PassResult` per pass
(duration, `cache_hit`, inputs, outputs, warnings), `artifacts_generated`, and `cache_hits`.
`commit_sha`, `publisher_result`, and `artifacts_reused` are present and Optional — the shape is
stable for when RepositoryState and caching fill them. Exposed at `GET /projects/{id}/compilation-report`.

**Forward compatibility for the scheduler (v1.0).** Passes are still executed sequentially, but the
executor reads only descriptors. A future DAG scheduler consumes the *same* descriptors —
`build_dependency_graph → topological_sort → run` — so no pass implementation changes when ordering
becomes derived rather than listed.

## Alternatives considered

- **Keep the runtime-validated dict.** Rejected: it can never offer startup guarantees; the failure
  mode is "bad data three passes later."
- **`dict` → typed object, strings as keys.** Rejected halfway: typing the container without typing
  the *keys* still validates on string equality and misses type mismatches.
- **Jump straight to the DAG scheduler.** Deferred to v1.0: the symbol table + descriptors are the
  prerequisite, and sequential execution is correct until pass count makes ordering a burden.

## Trade-offs

- (+) Ill-formed pipelines are impossible to *run* — the error moves from runtime to startup.
- (+) Every compile is observable: a build log with per-pass timing and provenance.
- (+) Descriptors are scheduler-ready; the sequential→DAG migration touches no pass.
- (−) More machinery around a still-linear pipeline — justified by the guarantees, and by how much
  of it RepositoryState/caching will reuse.
- (−) `cache_hit`/`artifacts_reused` are present but always zero/false until pass caching lands —
  deliberately, so the report shape doesn't churn later.

## Consequences

- `run_explain_pipeline` is now a thin wrapper over a validated `Compiler`; the explain endpoint is
  unchanged, and a new compilation-report endpoint surfaces the build log.
- This is the structural home the project's invariants needed: passes declare dependencies, the
  compiler proves them, and a run is observable. RepositoryState slots in as another typed key.

## Future revisit

DAG scheduling over the descriptors (v1.0), pass-output caching keyed on `cacheable` + input hash
(flipping `cache_hit`/`artifacts_reused` live), and `RepositorySyncPass` producing a
`RepositoryState` slot (Alpha-0.9) that fills `commit_sha` / `publisher_result` in the report.
