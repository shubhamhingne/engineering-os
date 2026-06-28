"""Structured JSON logging. Every AI action — and every request — is observable (Principle 4).

A `request_id` contextvar is set per request by the diagnostics middleware and folded into every log
line emitted while handling that request, so logs can be correlated without threading an id by hand."""
import contextvars
import json
import logging
import sys

# Set per-request by DiagnosticsMiddleware; included in every log line during that request.
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

_FIELDS = (
    "artifact_type",
    "version_no",
    "source",
    "provider",
    "model",
    "tokens_in",
    "tokens_out",
    "latency_ms",
    "method",
    "path",
    "status",
    "trace_id",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        request_id = request_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        for field in _FIELDS:
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        return json.dumps(payload)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
