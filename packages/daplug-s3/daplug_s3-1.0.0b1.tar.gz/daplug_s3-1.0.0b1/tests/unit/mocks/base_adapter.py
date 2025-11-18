"""Helpers that stand in for BaseAdapter behaviors during unit tests."""
from __future__ import annotations

from typing import Any, Dict, List


class PublishTracker:
    """Callable helper that records publish invocations."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def __call__(self, db_data: Dict[str, Any], **metadata: Any) -> None:  # type: ignore[override]
        self.calls.append({
            "data": db_data,
            "metadata": metadata,
        })

    def last(self) -> Dict[str, Any] | None:
        return self.calls[-1] if self.calls else None
