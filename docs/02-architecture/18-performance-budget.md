# 18 — Performance Budget

Explicit budgets, set now so they can be enforced in CI and load tests rather than discovered
in production. A budget exceeded is a regression, not a surprise.

## Latency budgets

| Operation | Budget | Notes |
|---|---|---|
| Non-AI API endpoint (p95) | < 300 ms | CRUD on projects/artifacts |
| Generation time-to-first-token (p95) | < 3 s | Streaming; perceived responsiveness |
| Full PRD generation (p95) | < 25 s | Streamed; user sees progress throughout |
| Repository export (p95) | < 10 s | Scaffold + create + push |
| Auth callback (p95) | < 1 s | Excluding GitHub round-trip |

## Frontend budgets (Core Web Vitals)

| Metric | Budget |
|---|---|
| LCP | < 2.5 s |
| INP | < 200 ms |
| CLS | < 0.1 |
| Initial JS (route, gzip) | < 200 KB |

## Throughput & concurrency (MVP)

- Sustain **50 concurrent active users** and **10 concurrent generations** on a single API +
  single worker without breaching latency budgets.
- Generations are queued; backpressure protects the providers and the budget.

## Resource budgets

| Resource | Budget (MVP) |
|---|---|
| API container memory | < 512 MB steady |
| DB connections | pooled, ≤ 20 |
| Redis | streaming buffers + queue only |

## Cost budgets (AI)

The metric most able to sink an AI product. Enforced as hard caps, not guidelines.

| Scope | Budget |
|---|---|
| Per generation | hard token cap per artifact type; default model is cost-efficient |
| Per user / day | rate-limited number of generations |
| Per environment / day | spend alert + automatic throttle on breach |

Model tiering exposes the cost/quality tradeoff to the user; expensive frontier models are
opt-in per generation.

## Enforcement

- **CI:** Lighthouse budget check on web; a smoke load test asserts API p95 budgets.
- **Runtime:** dashboards + alerts on TTFT, success rate, and daily spend ([17](17-observability.md)).
- **Code:** token caps and rate limits live in the generation module, not scattered.

## Future evolution

As load grows, budgets are re-baselined against the scaling path (horizontal workers, extracted
generation service — ADR-0001). Budgets are versioned with the architecture so regressions are
visible in review.
