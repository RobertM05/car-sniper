"""
Simple in-process metrics registry for car-sniper.
Provides counters and a @timed decorator; dumps summary on exit via atexit.

Usage:
    from backend.metrics import metrics
    metrics.increment("ads_scraped", 5)
    metrics.increment("errors", 1)

    @metrics.timed("scrape_olx")
    async def scrape_olx(...):
        ...
"""

import atexit
import time
import functools
import json
import sys
from typing import Dict


class MetricsRegistry:
    """Thread-safe-ish counters + timing summaries (in-process only)."""

    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.timings: Dict[str, list] = {}  # name -> [durations in seconds]
        atexit.register(self._dump_on_exit)

    # -- Counters ----------------------------------------------------------

    def increment(self, name: str, delta: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + delta

    def get(self, name: str) -> int:
        return self.counters.get(name, 0)

    # -- Timing decorator --------------------------------------------------

    def timed(self, name: str):
        """Decorator that records wall-clock duration of (a)sync functions."""

        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.monotonic()
                try:
                    return await func(*args, **kwargs)
                finally:
                    elapsed = time.monotonic() - start
                    self._record_timing(name, elapsed)

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.monotonic()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = time.monotonic() - start
                    self._record_timing(name, elapsed)

            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    def _record_timing(self, name: str, elapsed: float) -> None:
        if name not in self.timings:
            self.timings[name] = []
        self.timings[name].append(elapsed)

    # -- Dump --------------------------------------------------------------

    def _dump_on_exit(self) -> None:
        """Print a JSON summary of all metrics to stderr at process exit."""
        summary = {"counters": dict(self.counters), "timings": {}}
        for name, durations in self.timings.items():
            if durations:
                summary["timings"][name] = {
                    "count": len(durations),
                    "total_s": round(sum(durations), 4),
                    "avg_s": round(sum(durations) / len(durations), 4),
                    "min_s": round(min(durations), 4),
                    "max_s": round(max(durations), 4),
                }

        # Only emit if there's something to report
        if summary["counters"] or summary["timings"]:
            payload = {"type": "metrics_summary", "data": summary}
            print(json.dumps(payload, ensure_ascii=False, default=str), file=sys.stderr)


# Global singleton
metrics = MetricsRegistry()
