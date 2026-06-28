# Beta-readiness register

A living engineering-debt register from the Staff-Engineer readiness audit (public-beta bar). The
**feature set is frozen** ([compiler governance](../02-architecture/20-compiler-specification.md#governance));
this is the shift from feature development to **beta hardening**. Almost every item is operational
(implementation/config) — the compiler core and its contracts are beta-ready; the operational shell
around them is the remaining work.

> IDs use a `BR-` prefix (Beta-Readiness) to avoid colliding with the project's `edr-` **Engineering
> Decision Records**, which are a different artifact.

## Register

| ID | Finding | Type | Impact | Likelihood | Priority | Status | Target | Resolved in |
|---|---|---|---|---|---|---|---|---|
| BR-01 | CI runs `ruff`/`pytest` with `\|\| true` — never gates | Reliability | High | High | **Critical** | ✅ Resolved | Beta-0.1 | `4b79eb4` · alpha-0.3.1 · 2026-06-27 |
| BR-02 | GitHub OAuth tokens stored plaintext at rest | Security | High | High | **Critical** | ✅ Resolved | Beta-0.1 | `8c3e986` · alpha-0.3.1 · 2026-06-27 |
| BR-03 | No application Dockerfile / reproducible deploy path | Reliability | High | High | High | 🟡 Authored | Beta-0.2 | `1259459` · alpha-0.3.2 · build unverified (no Docker host) |
| BR-04 | No DB migrations (`create_all`, no Alembic) | Reliability | High | Medium | High | ✅ Resolved | Beta-0.2 | `cd22797` · alpha-0.3.2 · 2026-06-28 |
| BR-05 | No rate limiting on AI / OAuth endpoints | Security | High | Medium | High | ✅ Resolved | Beta-0.2 | `cd22797` · alpha-0.3.2 · 2026-06-28 |
| BR-06 | Static `/health`; no readiness vs liveness | Reliability | Medium | High | High | ✅ Resolved | Beta-0.2 | `cd22797` · alpha-0.3.2 · 2026-06-28 |
| BR-07 | Cookie/CORS prod hardening (`cookie_secure=False`) | Security | Medium | Medium | High | ✅ Resolved | Beta-0.2 | `cd22797` · alpha-0.3.2 · 2026-06-28 |
| BR-08 | Observability is AI-action-only (no req-IDs/metrics/traces) | Observability | Medium | High | Medium | Open | Beta-0.3 | — |
| BR-09 | No frontend tests; accessibility unverified | UX | Medium | High | Medium | Open | Beta-0.4 | — |
| BR-10 | No lockfile (version ranges only) | DX | Medium | Medium | Medium | Open | Beta-0.3 | — |
| BR-11 | `examples/` is a stub; no one-command bootstrap | DX | Low | High | Medium | Open | Beta-0.3 | — |
| BR-12 | Real GitHub reader does O(files) blob fetches | Performance | Medium | Low | Medium | Open | Beta-0.3 | — |
| BR-13 | OSS completeness: no `CODE_OF_CONDUCT`, no OpenAPI snapshot in CI | OSS | Low | Medium | Nice-to-have | Open | Beta-0.4 | — |
| BR-14 | Local toolchain is Python 3.9; project requires 3.12 (CI uses 3.12) | DX | Medium | Medium | Medium | Open | Beta-0.3 | — |

*Impact/Likelihood are pre-mitigation. On resolution, an item records its commit SHA, release, and date.*

## Notes per finding

- **BR-01** — `api-ci.yml` masks lint/test failures with `|| true` and a skeleton install fallback; a
  green badge means nothing. `web-ci.yml` is similarly non-gating (`npm ci || echo …`, all steps
  `--if-present`), but tightening it is blocked on BR-10/BR-09 (a lockfile + real frontend tests) — see
  the decision below.
- **BR-02** — `UserSession.github_token` is a cleartext column holding live `repo`-scoped tokens. The
  compiler boundary already keeps tokens out of the core, so the fix is contained in the identity layer.
- **BR-03/04/06/07** — answer "can I deploy this?": container image, schema migrations, real readiness,
  and secure-by-default prod config.
- **BR-05** — generation (model cost) and the OAuth callback need throttling before public exposure.
- **BR-08** — excellent structured AI logs exist; missing request correlation, latency/error metrics,
  and traces for beta triage.
- **BR-12** — already anticipated in [ADR-0015](../02-architecture/adr/0015-repository-state-sync-pass.md)
  (a committed manifest short-circuits per-blob fetches).
- **BR-14** — surfaced during the audit: the dev venv is 3.9.6 while `requires-python>=3.12`; the
  3.9-compatible `Optional[...]` style is why the code still runs locally, but the toolchains should align.

## What's already strong

Pre-commit with **gitleaks + detect-private-key + ruff/ruff-format**; Dependabot; CODEOWNERS;
structured AI observability; 95 backend tests including property-based hardening; the full
specification/invariants/history; and a compiler boundary that keeps secrets out of the core.

## Sprint 2 — Deployability

> **Mission:** any engineer can deploy Engineering OS into a production-like environment from a clean
> checkout using documented steps, with no manual intervention.
>
> **Success criteria:** ☐ image builds · ☐ containers start · ☑ migrations run automatically
> (`alembic upgrade head` verified on SQLite; wired into the container entrypoint) · ☑ readiness/
> liveness report correctly · ☑ secure production profile enforced · ☐ API responds after cold start.
> *(Checked items are verified here; the three unchecked require a Docker host — see metrics.)*
>
> **Exit criteria:** `docker compose up` (or `make up`) brings the stack up; `make dev` takes a fresh
> machine from zero to a running API; BR-03…BR-07 resolved.
>
> **Phases:** 1 Dockerfile → 2 Compose → 3 Alembic → 4 Health → 5 Production config → 6 Rate limiting
> *(deploy first, harden the deployed service last)*.

## Sprint metrics

| Metric | Sprint 1 → after | Sprint 2 → after |
|---|---|---|
| Tests | 95 → 97 | 97 → 105 |
| Coverage | — → 92% | 92% → 93% |
| Critical findings open | 2 → 0 | 0 → 0 |
| High findings open | 5 → 5 | 5 → 0 |
| Deployment time | N/A | **not measured** (no Docker host in this environment) |

## Sprints (hardening, not features)

1. **Trust (Critical):** BR-01, BR-02 → ✅ **shipped in `alpha-0.3.1`.**
2. **Deployability:** BR-04, BR-05, BR-06, BR-07 ✅ + BR-03 🟡 (authored; build pending a Docker host)
   → **shipped in `alpha-0.3.2`.**
3. **Operability:** BR-08, BR-10, BR-12, BR-14.
4. **Developer experience:** BR-11, frontend smoke (BR-09).
5. **Launch readiness:** BR-09 (a11y), BR-13, screenshots/demo, OpenAPI snapshot.

## Decision: web-ci stays non-gating until the frontend is real

Tightening `web-ci` now would replace a dishonest green with an undiagnosable red (no lockfile, no
tests, no Node verification here). It is intentionally left non-gating until BR-10 (lockfile) and
BR-09 (frontend tests) land, at which point it gates like `api-ci`. Honest-red beats fake-green, but
only when the red is actionable.
