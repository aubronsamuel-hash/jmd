"""FastAPI middleware wiring observability concerns."""

from __future__ import annotations

import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .context import reset_context, update_attributes
from .metrics import MetricsRegistry
from .tracing import ObservabilityTracer, trace


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Attach tracing, metrics and logging metadata on each request."""

    def __init__(
        self,
        app,
        *,
        tracer: ObservabilityTracer,
        metrics: MetricsRegistry,
        latency_threshold_seconds: float,
    ) -> None:
        super().__init__(app)
        self._tracer = tracer
        self._metrics = metrics
        self._latency_threshold_seconds = latency_threshold_seconds

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        trace_id = request.headers.get("X-Trace-Id") or uuid4().hex
        reset_context(trace_id)
        update_attributes(
            request_id=request.headers.get("X-Request-Id", trace_id),
            organization_id=request.headers.get("X-Organization-Id"),
            user_id=request.headers.get("X-User-Id"),
        )
        labels = {
            "method": request.method,
            "path": request.url.path,
        }
        start_time = time.perf_counter()
        response: Response | None = None
        status_code = 500
        with trace(
            self._tracer,
            "http.request",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        ) as span:
            try:
                response = await call_next(request)
            except Exception:
                status_code = 500
                span.set_attribute("http.status_code", status_code)
                raise
            else:
                status_code = response.status_code
                span.set_attribute("http.status_code", status_code)
            finally:
                duration = max(0.0, time.perf_counter() - start_time)
                span.set_attribute("http.duration", duration)
                self._metrics.observe(
                    "api_request_duration_seconds",
                    duration,
                    labels={**labels, "status": str(status_code)},
                )
                self._metrics.increment(
                    "api_request_total",
                    labels={**labels, "status": str(status_code)},
                )
                if status_code >= 500:
                    self._metrics.increment(
                        "api_request_errors_total",
                        labels={**labels, "status": str(status_code)},
                    )
        if response is None:
            response = Response(status_code=status_code)
        response.headers["X-Trace-Id"] = trace_id
        if duration > self._latency_threshold_seconds:
            response.headers.setdefault("X-Observability-Warning", "latency")
        return response


__all__ = ["ObservabilityMiddleware"]
