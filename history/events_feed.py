"""
Events feed module.

Maintains a chronological narrative list of notable happenings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EventsFeed:
    """Simple month-indexed narrative store."""

    entries: Dict[int, List[str]] = field(default_factory=dict)

    def add_event(self, month: int, description: str) -> None:
        self.entries.setdefault(month, []).append(description)

    def get_month_entries(self, month: int) -> List[str]:
        return self.entries.get(month, [])

    def as_chronological(self) -> List[tuple[int, List[str]]]:
        return sorted(self.entries.items(), key=lambda item: item[0])


