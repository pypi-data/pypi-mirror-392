from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Mapping, Sequence

from .di import DependencyContainer
from .exceptions import HTTPError
from .handlers import (
    HandlerSpec,
    build_handler_spec,
    build_request,
    execute_route,
)
from .metrics import MetricsRegistry
from .middleware import build_default_middleware
from .routing import RouteNotFound, Router
from .serializers import normalize_response
from .types import MiddlewareCallable, Receive, Request, Response, Scope, Send

LOGGER = logging.getLogger("quicky.app")


class Quicky:
    def __init__(
        self,
        *,
        middleware: Sequence[MiddlewareCallable] | None = None,
    ) -> None:
        self.router = Router()
        self.container = DependencyContainer()
        self.metrics = MetricsRegistry()
        self.middleware: list[MiddlewareCallable] = (
            list(middleware)
            if middleware
            else build_default_middleware(self.metrics)
        )
        self._spec_cache: dict[Callable[..., Any], HandlerSpec] = {}
        self.get("/metrics")(self._metrics_endpoint)

    def route(
        self,
        path: str,
        *,
        methods: Sequence[str] = ("GET",),
        name: str | None = None,
        summary: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            spec = build_handler_spec(func)
            self._spec_cache[func] = spec
            self.router.add_route(
                path,
                methods,
                func,
                name=name,
                summary=summary,
            )
            return func

        return decorator

    def get(
        self,
        path: str,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=("GET",), **kwargs)

    def post(
        self,
        path: str,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=("POST",), **kwargs)

    def put(
        self,
        path: str,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=("PUT",), **kwargs)

    def patch(
        self,
        path: str,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=("PATCH",), **kwargs)

    def delete(
        self,
        path: str,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=("DELETE",), **kwargs)

    def options(
        self,
        path: str,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=("OPTIONS",), **kwargs)

    def use(self, middleware: MiddlewareCallable) -> None:
        self.middleware.append(middleware)

    def dependency(
        self,
        key: Any,
        provider: Callable[..., Any],
        *,
        scope: str = "app",
    ) -> None:
        self.container.register(key, provider, scope=scope)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            raise NotImplementedError(
                "Quicky currently supports only HTTP scope"
            )
        request = build_request(scope, receive, send, self)
        try:
            route, params = self.router.match(request.method, request.path)
            spec = self._spec_cache[route.handler]
        except RouteNotFound:
            await self._send_response(
                _json_error(404, "Not Found"),
                send,
            )
            return
        except KeyError:
            spec = build_handler_spec(route.handler)
            self._spec_cache[route.handler] = spec
        handler = self._apply_middleware(route, spec, params)
        try:
            response = await handler(request)
        except HTTPError as exc:
            await self._send_response(
                _json_error(exc.status_code, exc.detail),
                send,
            )
            return
        except Exception as exc:  # pragma: no cover - safety net
            LOGGER.exception("Unhandled error: %s", exc)
            await self._send_response(
                _json_error(500, "Internal Server Error"),
                send,
            )
            return
        await self._send_response(response, send)

    def _apply_middleware(
        self,
        route,
        spec: HandlerSpec,
        params: Mapping[str, str],
    ) -> Callable[[Request], Awaitable[Response]]:
        async def endpoint(request: Request) -> Response:
            return await execute_route(
                route,
                spec,
                request,
                params,
                self.container,
            )

        handler = endpoint
        for middleware in reversed(self.middleware):
            next_handler = handler

            async def wrapper(
                request: Request,
                _middleware: MiddlewareCallable = middleware,
                _next: Callable[[Request], Awaitable[Response]] = next_handler,
            ) -> Response:
                return await _middleware(request, _next)

            handler = wrapper
        return handler

    async def _send_response(self, response: Response, send: Send) -> None:
        header_items = list(response.headers.items())
        has_content_type = any(
            key.lower() == "content-type"
            for key, _ in header_items
        )
        if response.media_type and not has_content_type:
            header_items.append(("content-type", response.media_type))
        elif not has_content_type:
            header_items.append(
                ("content-type", "application/octet-stream")
            )

        body_length = (
            len(response.body or b"")
            if response.stream is None
            else None
        )
        has_content_length = any(
            key.lower() == "content-length"
            for key, _ in header_items
        )
        if body_length is not None and not has_content_length:
            header_items.append(
                ("content-length", str(body_length))
            )

        headers = [
            (key.encode("latin-1"), value.encode("latin-1"))
            for key, value in header_items
        ]
        await send(
            {
                "type": "http.response.start",
                "status": response.status,
                "headers": headers,
            }
        )

        if response.stream is not None:
            async for chunk in response.stream:
                await send(
                    {
                        "type": "http.response.body",
                        "body": chunk,
                        "more_body": True,
                    }
                )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"",
                    "more_body": False,
                }
            )
            return

        await send(
            {
                "type": "http.response.body",
                "body": response.body or b"",
            }
        )

    async def _metrics_endpoint(self, request: Request) -> Response:
        payload = self.metrics.export_prometheus().encode("utf-8")
        response = Response(
            status=200,
            body=payload,
            headers={
                "content-type": "text/plain; version=0.0.4",
            },
        )
        return response


def _json_error(status: int, detail: str) -> Response:
    payload = {"detail": detail}
    response = normalize_response(
        (payload, status, {"content-type": "application/json"})
    )
    return response


__all__ = ["Quicky"]
