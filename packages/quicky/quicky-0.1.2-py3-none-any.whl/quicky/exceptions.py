from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HTTPError(Exception):
    status_code: int
    detail: str

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"


class ValidationError(HTTPError):
    def __init__(self, detail: str, *, status_code: int = 422):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(HTTPError):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=404, detail=detail)


__all__ = ["HTTPError", "ValidationError", "NotFoundError"]


