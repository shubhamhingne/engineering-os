# Release gates

Every beta-hardening release passes through the same gates. A gate is **PASS**, **NOT VERIFIED**
(no evidence yet — not a failure, an honesty marker), or **N/A**. A release ships when no gate is a
regression and the unmet gates are scheduled.

## `alpha-0.3.3` — Production Diagnostics

| Gate | Result | Evidence |
|---|---|---|
| Architecture | ✅ PASS | compiler core unchanged (fingerprint stable); all work in the operational shell |
| Security | ✅ PASS | tokens encrypted at rest; prod config guard; secret scanning |
| Deployment | 🟡 PASS* | migrations auto-run, health probes, compose stack — *image build pending a Docker host |
| Observability | ✅ PASS | request/trace IDs, structured access logs, Prometheus `/metrics` ([evidence](../05-demo/evidence/sprint-3.md)) |
| Tests | ✅ PASS | 110 passing, 93% coverage |
| Documentation | ✅ PASS | 0 broken links; specification, register, evidence current |
| Performance | ⏳ NOT VERIFIED | scheduled Sprint 5 (load test) |
| Accessibility | ⏳ NOT VERIFIED | scheduled Sprint 5 (needs Node) |

## History

| Release | Theme | Gates met |
|---|---|---|
| `alpha-0.3.1` | Trust | Security, Tests, CI |
| `alpha-0.3.2` | Deployability | Deployment*, Tests, Docs |
| `alpha-0.3.3` | Production Diagnostics | Observability, Tests, Docs |
