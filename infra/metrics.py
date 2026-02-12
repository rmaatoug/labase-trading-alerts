"""Minimal metrics helper for local use.

Provides a tiny in-process metrics collector with counters and gauges.
Designed for quick instrumentation in scripts in this repo (no external
dependencies).
"""
from typing import Dict, Any, Optional
import json


class Metrics:
    def __init__(self) -> None:
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}

    def inc(self, name: str, value: int = 1) -> None:
        """Increment a counter by `value`."""
        self._counters[name] = self._counters.get(name, 0) + int(value)

    def gauge(self, name: str, value: float) -> None:
        """Set a gauge to `value`."""
        self._gauges[name] = float(value)

    def snapshot(self) -> Dict[str, Any]:
        """Return a snapshot of current metrics."""
        return {"counters": dict(self._counters), "gauges": dict(self._gauges)}

    def flush(self, path: Optional[str] = None) -> None:
        """Flush metrics as JSON to `path` (append) or to stdout if None."""
        payload = json.dumps(self.snapshot())
        if path:
            with open(path, "a") as f:
                f.write(payload + "\n")
        else:
            print(payload)


__all__ = ["Metrics"]
