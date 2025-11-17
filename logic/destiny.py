"""
Destiny system helpers.

Encapsulates the global destiny strength slider and bias utilities that
gently influence desires, interactions, and narrative events.
"""

from __future__ import annotations

from parushini.agents.agent import Agent

DESTINY_STRENGTH: float = 50.0


def set_destiny_strength(value: float) -> None:
    """Configure the global destiny strength (0-100)."""
    global DESTINY_STRENGTH
    DESTINY_STRENGTH = max(0.0, min(100.0, value))


def get_destiny_bias(agent: Agent) -> float:
    """Compute an agent-specific destiny bias scalar."""
    blessing = getattr(agent, "destiny_blessing", 0.0)
    base = max(0.0, min(1.0, agent.destiny_seed + blessing))
    bias = base * (DESTINY_STRENGTH / 100.0)
    return max(0.0, min(1.5, bias))


def apply_destiny_bias(agent: Agent, value: float) -> float:
    """Nudge numeric values by destiny bias without exceeding [0, 100]."""
    bias = get_destiny_bias(agent)
    adjustment = (bias - 0.5) * 8.0  # roughly [-4, +8]
    return max(0.0, min(100.0, value + adjustment))


