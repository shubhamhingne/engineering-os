"""Prometheus metrics — the numbers you reach for when something breaks (Sprint 3).

HTTP throughput/latency/errors, and AI generation volume, tokens, cost, and latency by model. Exposed
at GET /metrics. Recording is cheap and side-effect-free; nothing here is on the compiler path."""
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

HTTP_REQUESTS = Counter(
    "eos_http_requests_total", "HTTP requests", ["method", "route", "status"]
)
HTTP_LATENCY = Histogram(
    "eos_http_request_duration_seconds", "HTTP request latency (s)", ["route"]
)
UNHANDLED_ERRORS = Counter(
    "eos_unhandled_errors_total", "Unhandled exceptions surfaced as 500s"
)

AI_GENERATIONS = Counter(
    "eos_ai_generations_total", "AI generations", ["provider", "model", "artifact_type"]
)
AI_TOKENS = Counter(
    "eos_ai_tokens_total", "AI tokens", ["provider", "model", "direction"]
)
AI_COST_USD = Counter(
    "eos_ai_cost_usd_total", "Estimated AI spend (USD)", ["provider", "model"]
)
AI_LATENCY = Histogram(
    "eos_ai_generation_duration_seconds", "AI generation latency (s)", ["provider", "model"]
)

# Illustrative price per 1K tokens (input, output), USD. Unknown/fake models cost 0.
_COST_PER_1K = {
    "claude-sonnet-4-6": (0.003, 0.015),
}


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    rate_in, rate_out = _COST_PER_1K.get(model, (0.0, 0.0))
    return (tokens_in / 1000) * rate_in + (tokens_out / 1000) * rate_out


def record_ai_generation(
    provider: str, model: str, artifact_type: str, tokens_in: int, tokens_out: int, latency_ms: int
) -> None:
    AI_GENERATIONS.labels(provider, model, artifact_type).inc()
    AI_TOKENS.labels(provider, model, "in").inc(tokens_in)
    AI_TOKENS.labels(provider, model, "out").inc(tokens_out)
    AI_COST_USD.labels(provider, model).inc(estimate_cost_usd(model, tokens_in, tokens_out))
    AI_LATENCY.labels(provider, model).observe(latency_ms / 1000)


def render_latest() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
