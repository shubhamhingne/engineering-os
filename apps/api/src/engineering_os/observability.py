"""Structured JSON logging. Every AI action is observable (Principle 4)."""
import json
import logging
import sys

_AI_FIELDS = (
    "artifact_type",
    "version_no",
    "source",
    "provider",
    "model",
    "tokens_in",
    "tokens_out",
    "latency_ms",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        for field in _AI_FIELDS:
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        return json.dumps(payload)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
