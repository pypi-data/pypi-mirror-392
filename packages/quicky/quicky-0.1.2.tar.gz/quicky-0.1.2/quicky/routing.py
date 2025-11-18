from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Sequence

from .types import Handler


@dataclass(slots=True)
class RoutePattern:
    path: str
    segments: tuple["Segment", ...]


@dataclass(slots=True)
class Segment:
    is_param: bool
    name: str


@dataclass(slots=True)
class Route:
    methods: frozenset[str]
    handler: Handler
    pattern: RoutePattern
    name: str | None = None
    summary: str | None = None


class RouteNotFound(RuntimeError):
    pass


def _compile_path(path: str) -> RoutePattern:
    if not path.startswith("/"):
        raise ValueError("Path must start with '/'")
    raw_segments = [segment for segment in path.strip("/").split("/") if segment]
    if not raw_segments and path == "/":
        return RoutePattern(path="/", segments=tuple())
    segments: list[Segment] = []
    for segment in raw_segments:
        if segment.startswith("{") and segment.endswith("}"):
            segments.append(Segment(is_param=True, name=segment[1:-1]))
        else:
            segments.append(Segment(is_param=False, name=segment))
    return RoutePattern(path=path, segments=tuple(segments))


class Router:
    def __init__(self) -> None:
        self._routes: list[Route] = []

    def add_route(
        self,
        path: str,
        methods: Sequence[str],
        handler: Handler,
        *,
        name: str | None = None,
        summary: str | None = None,
    ) -> None:
        pattern = _compile_path(path)
        normalized_methods = frozenset(method.upper() for method in methods)
        self._routes.append(
            Route(
                methods=normalized_methods,
                handler=handler,
                pattern=pattern,
                name=name,
                summary=summary,
            )
        )

    def match(self, method: str, path: str) -> tuple[Route, dict[str, str]]:
        normalized_method = method.upper()
        for route in self._routes:
            if normalized_method not in route.methods and not (
                normalized_method == "HEAD" and "GET" in route.methods
            ):
                continue
            params = _match_pattern(route.pattern, path)
            if params is not None:
                return route, params
        raise RouteNotFound(f"No route for {method} {path}")

    @property
    def routes(self) -> list[Route]:
        return list(self._routes)


def _match_pattern(pattern: RoutePattern, path: str) -> dict[str, str] | None:
    if pattern.path == "/" and path == "/":
        return {}
    path_segments = [segment for segment in path.strip("/").split("/") if segment]
    if len(path_segments) != len(pattern.segments):
        return None
    params: dict[str, str] = {}
    for segment, value in zip(pattern.segments, path_segments, strict=True):
        if not segment.is_param:
            if segment.name != value:
                return None
            continue
        params[segment.name] = value
    return params


__all__ = ["Route", "Router", "RouteNotFound"]


