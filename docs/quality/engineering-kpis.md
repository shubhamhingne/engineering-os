# Engineering KPIs

Measure engineering, not just features. Values are recorded per release where measurable; the rest
are wired and waiting on an environment that can produce them (a Docker host / load test). The point
is that each is *exposed by the system* — turning them into graphs is then mechanical.

| KPI | Current | Source | Trend |
|---|---|---|---|
| Tests | 110 | `pytest` | 95 → 97 → 105 → 110 |
| Coverage | 93% | `pytest --cov` | 92 → 93 → 93 |
| Critical debt open | 0 | register | 2 → 0 |
| High debt open | 0 | register | 5 → 0 |
| Unhandled-error count | exposed | `eos_unhandled_errors_total` | — |
| Request latency | exposed | `eos_http_request_duration_seconds` (histogram) | — |
| AI generation latency | exposed | `eos_ai_generation_duration_seconds` | — |
| AI token cost (USD) | exposed | `eos_ai_cost_usd_total` (per model) | — |
| Docker image size | ⏳ pending | needs a Docker host | — |
| Cold-start time | ⏳ pending | needs a Docker host | — |
| Build duration | ⏳ pending | CI on a Docker host | — |

"Exposed" means the metric is live at `/metrics`; it becomes a tracked KPI once scraped over time.
