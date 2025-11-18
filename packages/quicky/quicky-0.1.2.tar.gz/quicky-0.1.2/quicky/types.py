# pyright: reportMissingImports=false
from __future__ import annotations

from dataclasses import MISSING, dataclass, field
from enum import Enum
from typing import (
    Annotated,
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Generic,
    Mapping,
    MutableMapping,
    TypeVar,
)

import orjson  # type: ignore[import]

Scope = Dict[str, Any]
Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]


class ParamSource(str, Enum):
    PATH = "path"
    QUERY = "query"
    BODY = "body"
    HEADER = "header"
    DEPENDENCY = "dependency"


@dataclass(slots=True)
class ParameterInfo:
    source: ParamSource
    alias: str | None = None
    description: str | None = None
    is_required: bool = True
    default: Any = field(default=MISSING)


T = TypeVar("T")


class Path(Generic[T]):
    def __class_getitem__(cls, annotation: type[T]) -> Any:  # noqa: D401
        return Annotated[annotation, ParameterInfo(source=ParamSource.PATH)]


class Query(Generic[T]):
    def __class_getitem__(cls, annotation: type[T]) -> Any:
        return Annotated[annotation, ParameterInfo(source=ParamSource.QUERY)]


class Body(Generic[T]):
    def __class_getitem__(cls, annotation: type[T]) -> Any:
        return Annotated[annotation, ParameterInfo(source=ParamSource.BODY)]


class Header(Generic[T]):
    def __class_getitem__(cls, annotation: type[T]) -> Any:
        return Annotated[annotation, ParameterInfo(source=ParamSource.HEADER)]


Handler = Callable[..., Awaitable[Any]]
NextHandler = Callable[["Request"], Awaitable["Response"]]
MiddlewareCallable = Callable[["Request", NextHandler], Awaitable["Response"]]


@dataclass(slots=True)
class Request:
    scope: Scope
    receive: Receive
    send: Send
    method: str
    path: str
    query_params: Mapping[str, list[str]]
    headers: Mapping[str, str]
    state: MutableMapping[str, Any]
    app: Any
    _body: bytes | None = field(default=None, init=False)
    _json: Any = field(default=None, init=False)

    async def body(self) -> bytes:
        if self._body is not None:
            return self._body
        chunks: list[bytes] = []
        more_body = True
        while more_body:
            message = await self.receive()
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            if chunk:
                chunks.append(chunk)
            more_body = message.get("more_body", False)
        self._body = b"".join(chunks)
        return self._body

    async def json(self) -> Any:
        if self._json is not None:
            return self._json
        raw = await self.body()
        if not raw:
            self._json = None
            return None
        self._json = orjson.loads(raw)
        return self._json


@dataclass(slots=True)
class Response:
    status: int = 200
    body: bytes = b""
    headers: MutableMapping[str, str] = field(default_factory=dict)
    media_type: str | None = None
    stream: AsyncIterator[bytes] | None = None

    def set_content(
        self,
        content: bytes,
        media_type: str | None = None,
    ) -> None:
        self.body = content
        if media_type:
            self.media_type = media_type


ASGIApp = Callable[[Scope, Receive, Send], Coroutine[Any, Any, None]]

__all__ = [
    "ASGIApp",
    "Body",
    "Handler",
    "Header",
    "MiddlewareCallable",
    "NextHandler",
    "ParamSource",
    "ParameterInfo",
    "Path",
    "Query",
    "Request",
    "Response",
    "Scope",
]
