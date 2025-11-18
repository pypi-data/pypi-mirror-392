from __future__ import annotations

import asyncio
from typing import Any

import uvicorn

from .types import ASGIApp


async def serve(
    app: ASGIApp,
    *,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info",
) -> None:
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        loop="uvloop",
        http="httptools",
        reload=reload,
        workers=workers,
        log_level=log_level,
    )
    server = uvicorn.Server(config)
    await server.serve()


def run(
    app: ASGIApp,
    *,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info",
) -> None:
    asyncio.run(
        serve(
            app,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level,
        )
    )


__all__ = ["run", "serve"]


