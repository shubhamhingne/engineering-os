# Quality dashboard

A single snapshot of engineering health. Updated each release; the numbers are produced by running
the suite, not estimated.

| Signal | Status | Detail |
|---|---|---|
| Release | `alpha-0.3.6` | beta hardening, Sprint 6 (backend resilience) |
| Tests | ✅ 121 passing | backend; incl. property-based |
| Coverage | ✅ 92% | `pytest --cov` (defensive retry paths are network-only) |
| Resilience | ✅ Retry + backoff | external calls (AI providers, GitHub) |
| Performance | ✅ Budget guarded | compile-time regression test |
| Contract | ✅ API surface pinned | OpenAPI path + schema tests |
| CI (api) | ✅ Gating | lint + tests, no `\|\| true` |
| Lint | ✅ Passing | `ruff check` |
| Secret scanning | ✅ Passing | pre-commit `gitleaks` + `detect-private-key` |
| Doc links | ✅ 0 broken | `check-doc-links.py` |
| Observability | ✅ Request-ID · metrics · trace-ID | `/metrics`, structured access logs |
| Security (tokens) | ✅ Encrypted at rest | Fernet; prod requires key |
| Docker image | 🟡 Pending verification | authored; needs a Docker host to build |
| Accessibility | ⏳ Pending | Sprint 5 (needs Node) |
| Performance | ⏳ Pending | Sprint 5 (load test) |
| Developer experience | ✅ `make setup`→`make test` (2 cmds, 0 edits) | [DX KPIs](dx-kpis.md) · runnable `make example` |
| Technical debt | 8 closed · 4 partial · 5 open | see [register](../08-decisions/beta-readiness-register.md) |

Legend: ✅ verified · 🟡 done but unverified here · ⏳ scheduled.
