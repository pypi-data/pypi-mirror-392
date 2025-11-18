from __future__ import annotations

import gzip
import json
import logging
import time
import uuid
from typing import Awaitable, Callable

from .metrics import MetricsRegistry
from .types import MiddlewareCallable, Request, Response

LOGGER = logging.getLogger("quicky")


def build_default_middleware(metrics: MetricsRegistry) -> list[MiddlewareCallable]:
    return [
        request_id_middleware,
        lambda request, call_next: metrics_middleware(request, call_next, metrics),
        logging_middleware,
        compression_middleware,
    ]


async def request_id_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    request_id = request.headers.get("x-request-id", uuid.uuid4().hex)
    request.state["request_id"] = request_id
    response = await call_next(request)
    response.headers.setdefault("x-request-id", request_id)
    return response


async def logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    LOGGER.info(
        json.dumps(
            {
                "event": "request_completed",
                "method": request.method,
                "path": request.path,
                "status": response.status,
                "duration_ms": round(duration_ms, 3),
                "request_id": request.state.get("request_id"),
            }
        )
    )
    return response


async def metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
    metrics: MetricsRegistry,
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    metrics.observe_request(
        method=request.method,
        path=request.path,
        status=response.status,
        duration=time.perf_counter() - start,
    )
    return response


async def compression_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    accept_encoding = request.headers.get("accept-encoding", "")
    if "gzip" not in accept_encoding or response.stream is not None:
        return response
    if len(response.body) < 512:
        return response
    response.body = gzip.compress(response.body)
    response.headers["content-encoding"] = "gzip"
    response.headers["vary"] = "Accept-Encoding"
    response.headers["content-length"] = str(len(response.body))
    return response


__all__ = ["build_default_middleware"]


