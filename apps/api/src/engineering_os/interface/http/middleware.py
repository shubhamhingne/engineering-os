"""Diagnostics middleware (Sprint 3) — request correlation, access logs, and HTTP metrics.

A pure-ASGI middleware (not BaseHTTPMiddleware) so it never buffers a response — SSE streaming stays
intact. Per request it: assigns/propagates an X-Request-ID, times the request, records throughput and
latency metrics, and emits one structured access log with the correlation id attached."""
import logging
import time
import uuid

from ...metrics import HTTP_LATENCY, HTTP_REQUESTS
from ...observability import request_id_var

access_log = logging.getLogger("eos.access")


def _incoming_request_id(scope) -> str:
    for name, value in scope.get("headers", []):
        if name == b"x-request-id" and value:
            return value.decode("latin-1")
    return ""


def _route_label(scope) -> str:
    route = scope.get("route")
    path_format = getattr(route, "path_format", None)
    if path_format:
        return path_format
    return scope.get("path", "unknown") if scope.get("route") else "unmatched"


class DiagnosticsMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _incoming_request_id(scope) or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        status = {"code": 500}

        async def send_wrapper(message) -> None:
            if message["type"] == "http.response.start":
                status["code"] = message["status"]
                message.setdefault("headers", []).append(
                    (b"x-request-id", request_id.encode("latin-1"))
                )
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.perf_counter() - start
            route = _route_label(scope)
            HTTP_REQUESTS.labels(scope.get("method", "-"), route, str(status["code"])).inc()
            HTTP_LATENCY.labels(route).observe(duration)
            access_log.info(
                "http.request",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status": status["code"],
                    "latency_ms": int(duration * 1000),
                },
            )
            request_id_var.reset(token)
