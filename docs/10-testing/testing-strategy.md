# Testing Strategy

Tests exist to let us change the system with confidence. We test **behavior**, not
implementation, and we put the most tests where they're cheapest and most valuable.

## The pyramid

```
        ╱ e2e ╲          few — critical user journeys (idea → repo)
      ╱ integration ╲    some — module + real DB, adapter contracts
    ╱     unit        ╲  many — domain logic, pure functions, ports via fakes
```

## Where tests live

- **Unit + integration:** beside the code, in `apps/web` and `apps/api`.
- **End-to-end / cross-cutting:** `tests/` at the repo root.

## What we test, by layer

| Layer | Approach |
|---|---|
| Domain / modules (api) | Unit tests with **fake adapters** behind the ports — fast, deterministic |
| Adapters (AI, GitHub, DB) | Integration/contract tests against a real or recorded boundary |
| API endpoints | Integration tests (FastAPI test client + test DB) |
| UI components | Unit tests (render + interaction) against design-system contracts |
| Critical journeys | A few e2e tests: create project → generate → export |

## Testing the AI (the hard part)

AI is non-deterministic, so we make it **testable by isolation** (Principle 2 + 5):

- The `AIProviderPort` has a **fake adapter** returning fixed responses → domain logic is tested
  deterministically without calling a provider.
- Adapter tests use **recorded fixtures** (canned provider responses) to verify parsing/streaming.
- We assert on **observable effects** (a versioned artifact created; a run record with tokens/cost),
  not on exact generated prose.

## Quality gates (CI)

- `web-ci` and `api-ci` must pass: lint, type-check, tests, build.
- New behavior requires tests; PRs without them are sent back.
- Tests must be **deterministic** — no real network, time, or randomness in unit tests.
- Target coverage on core domain logic ≥ 80% (a floor, not a goal; coverage ≠ correctness).

## Out of scope (for now)

Load/performance testing is budget-driven ([performance budget](../02-architecture/18-performance-budget.md))
and added when the generation path is implemented, not before.
