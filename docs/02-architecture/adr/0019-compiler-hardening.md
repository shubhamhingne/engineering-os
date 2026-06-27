# 0019 — Compiler hardening: property-based invariant testing

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Lead Architect
- **Related:** [ADR-0013](0013-typed-compiler-context.md), [ADR-0014](0014-compiler-fingerprint-and-dependency-graph.md), [ADR-0017](0017-dependency-driven-execution.md), [ADR-0018](0018-build-manifest.md)

## Context

The compiler now has enough invariants that manually enumerating example tests is less effective than
*describing properties* and letting a generator attack them. This is the point where adding capability
yields less than proving the existing guarantees. This release adds no feature — it tries to break the
invariants under hostile, randomly generated conditions.

## Decision

Add **Hypothesis** (a dev dependency) and a synthetic-pipeline generator: passes over `str`-valued
slots whose dependencies form a random acyclic graph over two independent seed inputs. Express the
compiler's guarantees as properties:

1. **DAG correctness** — a random valid pipeline validates, executes (every dependency satisfied), and
   its dependency graph is identical across serialization.
2. **Cycle / back-edge detection** — injecting a back edge always fails startup validation; an explicit
   two-node cycle is caught by `find_cycle`.
3. **Manifest identity** — a cold build and a fully-cached rebuild of the same inputs yield the same
   `manifest_hash` (equivalent artifacts ⇒ equivalent manifest).
4. **Fingerprint stability & sensitivity** — the fingerprint is stable across calls and changes when a
   single pass version is bumped.
5. **Cache correctness** — execute → cache → reuse reproduces every output identically; the warm run
   reuses everything.
6. **Dependency pruning** — after priming, changing exactly one input requires *exactly* the forward
   closure of that input through the consume edges, and reuses the rest.

Plus a non-property **replay-identity** test: rebuilding from the same inputs reproduces the manifest —
the receipt is sufficient to identify the build.

This also pins two distinctions in code as invariants: **cacheable ⇒ deterministic** and **execution
plans are side-effect-free** (planning peeks, never mutates cache stats).

## Alternatives considered

- **More example-based tests.** Rejected as the primary tool: examples cover points; properties cover
  the space. The existing example tests stay (they're precise and fast); properties are added on top.
- **A bespoke fuzzer.** Rejected: Hypothesis gives shrinking, reproducibility, and stateful strategies
  for free; a hand-rolled generator would reinvent them worse.

## Trade-offs

- (+) The invariants are now *demonstrated* over generated pipelines, not asserted on a few examples —
  the difference between "a prototype" and "a compiler."
- (+) Shrinking turns any future regression into a minimal counterexample automatically.
- (−) One new dev dependency and slightly slower test runs (~0.8s for the suite) — well worth it.
- (−) Synthetic passes use `str` slots, not real graphs; they exercise the *machinery* (validation,
  caching, pruning, identity), while the real-pipeline example tests cover semantics.

## Consequences

- New invariant: **equivalent artifacts imply equivalent manifests** (the semantic-identity property
  from ADR-0018, now generated-tested).
- The invariants document is reorganized from a numbered list into **categories** (Compiler, Artifacts,
  Execution, Identity) — they have become part of the architecture and categories scale past a list.

## Future revisit

A teachability pass next: a single document that explains the compiler model, invariants, execution,
identity, and extension model well enough that a senior engineer can predict where a new feature belongs
before reading the code. Then AI-backed pass implementations behind the contract, and compiler replay.
