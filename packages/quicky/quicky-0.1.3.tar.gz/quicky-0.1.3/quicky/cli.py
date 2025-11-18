from __future__ import annotations

import argparse
import importlib
import os
from typing import Any

from .runtime import run


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Quicky applications"
    )
    parser.add_argument(
        "app",
        help="Python path to the app instance, e.g. module:app",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("QUICKY_HOST", "0.0.0.0"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("QUICKY_PORT", "8000")),
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable autoreload",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("QUICKY_WORKERS", "1")),
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("QUICKY_LOG_LEVEL", "info"),
    )
    return parser


def load_app(path: str) -> Any:
    if ":" not in path:
        raise ValueError("App path must be in format 'module:attribute'")
    module_name, attribute = path.split(":", 1)
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attribute)
    except AttributeError as exc:  # pragma: no cover - defensive
        message = (
            f"Attribute {attribute!r} not found "
            f"in module {module_name!r}"
        )
        raise RuntimeError(message) from exc


def main(argv: list[str] | None = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)
    app = load_app(args.app)
    run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level,
    )


__all__ = ["main"]
