# pyright: reportMissingImports=false
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Annotated, Any, Mapping, Optional, get_args, get_origin
from urllib.parse import parse_qs

from pydantic import (  # type: ignore[import]
    TypeAdapter as PydanticTypeAdapter,
)
from pydantic_core import (  # type: ignore[import]
    ValidationError as PydanticValidationError,
)

from .di import DependencyContainer, DependencyNotFound
from .exceptions import HTTPError, ValidationError
from .routing import Route
from .serializers import normalize_response
from .types import (
    PARAM_DEFAULT_UNSET,
    ParamSource,
    ParameterInfo,
    Request,
    Response,
    Scope,
    Receive,
    Send,
)

UNSET = object()


@dataclass(slots=True)
class ParameterSpec:
    name: str
    source: ParamSource
    adapter: Optional[PydanticTypeAdapter[Any]]
    alias: str
    default: Any = UNSET
    dependency_key: Any | None = None
    is_request: bool = False


@dataclass(slots=True)
class HandlerSpec:
    parameters: tuple[ParameterSpec, ...]


def build_handler_spec(handler: Any) -> HandlerSpec:
    signature = inspect.signature(handler)
    hints = inspect.get_annotations(handler, eval_str=True)
    parameters: list[ParameterSpec] = []

    for name, parameter in signature.parameters.items():
        annotation = hints.get(name, parameter.annotation)
        resolved_type, metadata = _extract_parameter_info(annotation)
        default = (
            parameter.default
            if parameter.default is not inspect._empty
            else UNSET
        )

        if resolved_type is Request:
            parameters.append(
                ParameterSpec(
                    name=name,
                    source=ParamSource.DEPENDENCY,
                    adapter=None,
                    alias=name,
                    default=default,
                    dependency_key=Request,
                    is_request=True,
                )
            )
            continue

        if metadata is None:
            dep_key = (
                resolved_type
                if resolved_type is not inspect._empty
                else name
            )
            parameters.append(
                ParameterSpec(
                    name=name,
                    source=ParamSource.DEPENDENCY,
                    adapter=None,
                    alias=name,
                    default=default,
                    dependency_key=dep_key,
                )
            )
            continue

        adapter = PydanticTypeAdapter(resolved_type)
        alias = metadata.alias or name
        default_value = default
        if default_value is UNSET and metadata.default is not PARAM_DEFAULT_UNSET:
            default_value = metadata.default
        parameters.append(
            ParameterSpec(
                name=name,
                source=metadata.source,
                adapter=adapter,
                alias=alias,
                default=default_value if default_value is not UNSET else UNSET,
            )
        )
    return HandlerSpec(parameters=tuple(parameters))


def _extract_parameter_info(
    annotation: Any,
) -> tuple[Any, ParameterInfo | None]:
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        base_type = args[0]
        for meta in args[1:]:
            if isinstance(meta, ParameterInfo):
                return base_type, meta
    return annotation, None


def build_request(
    scope: Scope,
    receive: Receive,
    send: Send,
    app: Any,
) -> Request:
    query_bytes = scope.get("query_string", b"")
    query_params = parse_qs(
        query_bytes.decode("latin-1"),
        keep_blank_values=True,
    )
    headers = {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in scope.get("headers", [])
    }
    state = scope.setdefault("state", {})
    return Request(
        scope=scope,
        receive=receive,
        send=send,
        method=scope["method"],
        path=scope["path"],
        query_params=query_params,
        headers=headers,
        state=state,
        app=app,
    )


async def execute_route(
    route: Route,
    spec: HandlerSpec,
    request: Request,
    path_params: Mapping[str, str],
    container: DependencyContainer,
) -> Response:
    kwargs: dict[str, Any] = {}
    body_cache: Any = UNSET

    for parameter in spec.parameters:
        value = UNSET
        match parameter.source:
            case ParamSource.PATH:
                value = path_params.get(parameter.alias, UNSET)
            case ParamSource.QUERY:
                raw = request.query_params.get(parameter.alias)
                if raw is None:
                    value = UNSET
                elif len(raw) == 1:
                    value = raw[0]
                else:
                    value = raw
            case ParamSource.BODY:
                if body_cache is UNSET:
                    body_cache = await request.json()
                if parameter.alias == parameter.name:
                    value = body_cache
                else:
                    payload = body_cache or {}
                    if not isinstance(payload, Mapping):
                        raise ValidationError(
                            detail=(
                                "Body payload must be an object "
                                "for aliased fields"
                            ),
                        )
                    value = payload.get(parameter.alias)
            case ParamSource.HEADER:
                value = request.headers.get(parameter.alias.lower())
            case ParamSource.DEPENDENCY:
                if parameter.is_request:
                    kwargs[parameter.name] = request
                    continue
                value = await _resolve_dependency(
                    parameter,
                    container,
                    request,
                )

        coerced = _coerce_value(parameter, value)
        kwargs[parameter.name] = coerced

    result = route.handler(**kwargs)
    if inspect.isawaitable(result):
        result = await result  # type: ignore[assignment]
    return normalize_response(result)


async def _resolve_dependency(
    parameter: ParameterSpec,
    container: DependencyContainer,
    request: Request,
) -> Any:
    try:
        key = parameter.dependency_key or parameter.name
        return await container.resolve(key, request)
    except DependencyNotFound as exc:
        if parameter.default is not UNSET:
            return parameter.default
        raise HTTPError(status_code=500, detail=str(exc)) from exc


def _coerce_value(parameter: ParameterSpec, value: Any) -> Any:
    if value is UNSET:
        if parameter.default is not UNSET:
            return parameter.default
        raise ValidationError(detail=f"Missing value for '{parameter.name}'")
    if value is None and parameter.default is not UNSET:
        return parameter.default
    if parameter.adapter is None:
        return value
    try:
        return parameter.adapter.validate_python(value)
    except PydanticValidationError as exc:  # pragma: no cover
        raise ValidationError(detail=str(exc)) from exc


__all__ = ["build_handler_spec", "build_request", "execute_route"]
