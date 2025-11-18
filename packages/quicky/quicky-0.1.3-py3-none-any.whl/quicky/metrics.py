from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class LatencyStat:
    total: float = 0.0
    count: int = 0
    max_latency: float = 0.0

    def add(self, value: float) -> None:
        self.total += value
        self.count += 1
        if value > self.max_latency:
            self.max_latency = value


class MetricsRegistry:
    def __init__(self) -> None:
        self._request_counters: Dict[Tuple[str, str, int], int] = defaultdict(int)
        self._latency: Dict[Tuple[str, str], LatencyStat] = defaultdict(LatencyStat)

    def observe_request(self, *, method: str, path: str, status: int, duration: float) -> None:
        self._request_counters[(method, path, status)] += 1
        self._latency[(method, path)].add(duration)

    def export_prometheus(self) -> str:
        lines = [
            "# HELP quicky_requests_total Total number of processed requests",
            "# TYPE quicky_requests_total counter",
        ]
        for (method, path, status), count in sorted(self._request_counters.items()):
            lines.append(
                f'quicky_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
            )

        lines.extend(
            [
                "# HELP quicky_request_latency_seconds Request latency in seconds",
                "# TYPE quicky_request_latency_seconds summary",
            ]
        )
        for (method, path), stat in sorted(self._latency.items()):
            avg = stat.total / stat.count if stat.count else 0.0
            lines.append(
                f'quicky_request_latency_seconds_sum{{method="{method}",path="{path}"}} {stat.total:.6f}'
            )
            lines.append(
                f'quicky_request_latency_seconds_count{{method="{method}",path="{path}"}} {stat.count}'
            )
            lines.append(
                f'quicky_request_latency_seconds_max{{method="{method}",path="{path}"}} {stat.max_latency:.6f}'
            )
            lines.append(
                f'quicky_request_latency_seconds_avg{{method="{method}",path="{path}"}} {avg:.6f}'
            )
        return "\n".join(lines) + "\n"


__all__ = ["MetricsRegistry"]


