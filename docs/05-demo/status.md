# Project status

The executive dashboard — one screen, updated every release. For the engineering detail behind each
row, follow the link.

| | |
|---|---|
| **Current release** | `alpha-0.3.5` (beta hardening · launch readiness) · v1.0 compiler core |
| **Project health** | 🟢 Healthy |
| **Architecture** | ✅ Complete — [specification](../02-architecture/20-compiler-specification.md) |
| **Compiler** | 🔒 Frozen — [governance](../02-architecture/20-compiler-specification.md#governance) |
| **Backend** | ✅ 110 tests · 93% coverage |
| **Frontend** | ⏳ Implemented, untested here (needs Node) |
| **Deployment** | 🟡 Authored — Dockerfile + compose + migrations; image build pending a Docker host |
| **Diagnostics** | ✅ Verified — request/trace IDs · `/metrics` · [evidence](evidence/sprint-3.md) |
| **Developer experience** | ✅ Verified — `make setup` → `make test` ([DX KPIs](../quality/dx-kpis.md)) |
| **Accessibility** | ⏳ Pending — audit needs a browser |
| **Performance** | ⏳ Pending — load test / Lighthouse |
| **Security** | ✅ Tokens encrypted at rest · prod config guard · secret scanning |
| **Open findings** | 5 open · 4 partial · 8 closed — [register](../08-decisions/beta-readiness-register.md) |
| **Next milestone** | Public beta (after launch-readiness verification on real infra) |

Legend: ✅ verified · 🟡 done but unverified in this environment · ⏳ scheduled · 🔒 frozen.

## Verification environment note

This dashboard distinguishes **designed / implemented / verified**. Items marked 🟡 or ⏳ are not
incomplete code — they require infrastructure not present where the work was authored (a Docker
daemon, Node, a browser). They are owner-run on real infrastructure and tracked in the
[readiness register](../08-decisions/beta-readiness-register.md).
