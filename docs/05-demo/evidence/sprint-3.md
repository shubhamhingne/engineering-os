# Production evidence — Sprint 3 (Production Diagnostics)

Captured outputs, not claims. The rule: *verify, don't assume.* Everything below was produced by
running the system on this machine; items needing a Docker host are marked pending.

## Tests & coverage
```
110 passed
TOTAL coverage 93%
```

## Migrations run automatically (BR-04)
```
$ DATABASE_URL=sqlite:///./db alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade  -> 57dfc783ac41, initial schema
```

## Health probes (BR-06)
```
GET /health/live  -> 200 {'status': 'ok'}
GET /health/ready -> 200 {'status': 'ready'}     # runs SELECT 1; 503 until the DB answers
X-Request-ID echoed: demo-123                     # incoming correlation id is propagated
```

## Structured access log (one line per request, correlated)
```json
{"level":"INFO","logger":"eos.access","msg":"http.request","request_id":"cb26ea2d...",
 "method":"GET","path":"/health/live","status":200,"latency_ms":1}
```

## Prometheus `/metrics` sample (selected series)
```
eos_http_requests_total{method="POST",route="/api/v1/projects/{project_id}/artifacts/{artifact_type}",status="201"} 2.0
eos_ai_generations_total{artifact_type="vision",model="fake-1",provider="fake"} 2.0
eos_ai_tokens_total{direction="in",model="fake-1",provider="fake"} 20.0
eos_ai_tokens_total{direction="out",model="fake-1",provider="fake"} 92.0
eos_ai_cost_usd_total{model="fake-1",provider="fake"} 0.0
```
Routes are labelled by their *template* (low cardinality); AI cost is tracked per model (zero for the
fake provider, priced for real models).

## Trace ids on failure
An unhandled exception returns `{"detail":"internal server error","trace_id":"<32-hex>"}` and logs the
same `trace_id` with the request's `request_id` — a production error is findable from the response alone.

## Pending (require a Docker host)
- `docker build` log · container cold-start time · image size — not measurable in this environment.
