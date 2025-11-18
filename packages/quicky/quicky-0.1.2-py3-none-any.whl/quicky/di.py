from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Hashable

from .types import Request

ScopeType = str


@dataclass(slots=True)
class Provider:
    factory: Callable[..., Any]
    scope: ScopeType = "app"


class DependencyNotFound(RuntimeError):
    def __init__(self, key: Hashable):
        super().__init__(f"Dependency for {key!r} is not registered")
        self.key = key


class DependencyContainer:
    def __init__(self) -> None:
        self._providers: Dict[Hashable, Provider] = {}
        self._app_cache: Dict[Hashable, Any] = {}

    def register(
        self,
        key: Hashable,
        factory: Callable[..., Any],
        *,
        scope: ScopeType = "app",
    ) -> None:
        self._providers[key] = Provider(factory=factory, scope=scope)

    async def resolve(self, key: Hashable, request: Request) -> Any:
        provider = self._providers.get(key)
        if provider is None:
            raise DependencyNotFound(key)
        if provider.scope == "app":
            if key in self._app_cache:
                return self._app_cache[key]
            instance = provider.factory()
            if inspect.isawaitable(instance):
                instance = await instance  # type: ignore[assignment]
            self._app_cache[key] = instance
            return instance
        if provider.scope == "request":
            instance = provider.factory(request)
            if inspect.isawaitable(instance):
                instance = await instance  # type: ignore[assignment]
            return instance
        instance = provider.factory(request)
        if inspect.isawaitable(instance):
            instance = await instance  # type: ignore[assignment]
        return instance

    def unregister(self, key: Hashable) -> None:
        self._providers.pop(key, None)
        self._app_cache.pop(key, None)


__all__ = ["DependencyContainer", "DependencyNotFound"]


