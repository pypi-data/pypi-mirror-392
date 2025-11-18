# pyright: reportMissingImports=false
from __future__ import annotations

import inspect
from typing import Any, Mapping

import orjson  # type: ignore[import]

from .types import Response

JSON_OPTIONS = orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY


def normalize_response(value: Any) -> Response:
    if isinstance(value, Response):
        return value

    body = value
    status = 200
    headers: Mapping[str, str] | None = None

    if isinstance(value, tuple):
        body = value[0]
        if len(value) > 1:
            status = value[1]
        if len(value) > 2:
            headers = dict(value[2])

    if isinstance(body, Response):
        if headers:
            body.headers.update(headers)
        if status != 200:
            body.status = status
        return body

    if body is None:
        return Response(status=204, body=b"", headers=dict(headers or {}))

    if isinstance(body, (bytes, bytearray, memoryview)):
        return Response(
            status=status,
            body=bytes(body),
            headers=_materialize_headers(headers),
            media_type="application/octet-stream",
        )

    if isinstance(body, str):
        return Response(
            status=status,
            body=body.encode("utf-8"),
            headers=_materialize_headers(headers),
            media_type="text/plain; charset=utf-8",
        )

    if _is_async_iterable(body):
        return Response(
            status=status,
            headers=_materialize_headers(headers),
            media_type="application/octet-stream",
            stream=body,  # type: ignore[arg-type]
        )

    payload = orjson.dumps(body, option=JSON_OPTIONS)
    return Response(
        status=status,
        body=payload,
        headers=_materialize_headers(headers),
        media_type="application/json",
    )


def _is_async_iterable(value: Any) -> bool:
    if hasattr(value, "__aiter__"):
        return True
    return inspect.isasyncgen(value)


def _materialize_headers(headers: Mapping[str, str] | None) -> dict[str, str]:
    return dict(headers or {})


__all__ = ["normalize_response"]
