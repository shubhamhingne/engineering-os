# Quality dashboard

A single snapshot of engineering health. Updated each release; the numbers are produced by running
the suite, not estimated.

| Signal | Status | Detail |
|---|---|---|
| Release | `alpha-0.3.3` | beta hardening, Sprint 3 |
| Tests | ✅ 110 passing | backend; incl. property-based |
| Coverage | ✅ 93% | `pytest --cov` |
| CI (api) | ✅ Gating | lint + tests, no `\|\| true` |
| Lint | ✅ Passing | `ruff check` |
| Secret scanning | ✅ Passing | pre-commit `gitleaks` + `detect-private-key` |
| Doc links | ✅ 0 broken | `check-doc-links.py` |
| Observability | ✅ Request-ID · metrics · trace-ID | `/metrics`, structured access logs |
| Security (tokens) | ✅ Encrypted at rest | Fernet; prod requires key |
| Docker image | 🟡 Pending verification | authored; needs a Docker host to build |
| Accessibility | ⏳ Pending | Sprint 5 (needs Node) |
| Performance | ⏳ Pending | Sprint 5 (load test) |
| Technical debt | 7 closed · 1 authored · 6 open | see [register](../08-decisions/beta-readiness-register.md) |

Legend: ✅ verified · 🟡 done but unverified here · ⏳ scheduled.
