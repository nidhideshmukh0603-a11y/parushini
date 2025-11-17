"""
Diary engine for agents.

Generates short narrative entries based on month-to-month changes.
"""

from __future__ import annotations

from typing import Dict, List

from parushini.agents.agent import Agent
from parushini.logic.destiny import get_destiny_bias


TRACKED_FIELDS = ["love", "career", "social", "intelligence", "physical", "energy"]


def generate_monthly_diary(
    agent: Agent,
    month: int,
    interactions: List[str],
    events: List[str],
) -> str:
    """
    Create a diary entry highlighting state deltas, trauma, and destiny hints.
    """
    lines: List[str] = [f"Month {month}: "]
    changes = _summarize_state_changes(agent)
    if changes:
        lines.append(changes)
    if interactions:
        lines.append(f"Key moments: {interactions[0]}")
        if len(interactions) > 1:
            lines.append("More ripples followed.")
    if agent.trauma_level > 60:
        lines.append("Trauma feels heavy; breath work is urgent.")
    elif agent.trauma_level > 30:
        lines.append("Old wounds ache but remain manageable.")
    if events:
        lines.append(f"Destiny feed whispers: {events[-1]}")
    destiny_bias = get_destiny_bias(agent)
    if destiny_bias > 0.8:
        lines.append("Destiny hums loudly; choices feel guided.")
    elif destiny_bias < 0.2:
        lines.append("Destiny is quiet; free will feels wide open.")
    entry = " ".join(lines).strip()
    agent.last_state_snapshot = agent._capture_state_snapshot()
    return entry


def _summarize_state_changes(agent: Agent) -> str:
    """Describe notable state deltas."""
    previous = agent.last_state_snapshot or {}
    deltas: Dict[str, float] = {}
    for field in TRACKED_FIELDS:
        prev = previous.get(field)
        curr = getattr(agent, field)
        if prev is None:
            continue
        delta = curr - prev
        if abs(delta) >= 3.0:
            deltas[field] = delta
    if not deltas:
        return ""
    phrases = []
    for field, delta in deltas.items():
        direction = "rose" if delta > 0 else "fell"
        phrases.append(f"{field.capitalize()} {direction} by {abs(delta):.0f}")
    return ", ".join(phrases) + "."


