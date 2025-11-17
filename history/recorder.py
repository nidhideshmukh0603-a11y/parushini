"""
Recorder module.

This module handles recording of simulation events, agent states,
and interactions for later analysis and replay.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from parushini.core.simulator import World


@dataclass
class AgentSnapshot:
    """
    Snapshot of an agent's state at a specific month.
    
    Attributes:
        month: The month this snapshot was taken
        label: Agent's label identifier
        name: Agent's name
        physical: Physical state value (0-100)
        love: Love state value (0-100)
        career: Career state value (0-100)
        social: Social state value (0-100)
        intelligence: Intelligence state value (0-100)
        energy: Energy state value (0-100)
        trauma_level: Trauma level (0-100)
    """
    month: int
    label: str
    name: str
    physical: float
    love: float
    career: float
    social: float
    intelligence: float
    energy: float
    trauma_level: float


@dataclass
class WorldHistory:
    """
    History of world state snapshots over time.
    
    Attributes:
        snapshots: List of AgentSnapshot instances, one per agent per month
    """
    snapshots: List[AgentSnapshot] = field(default_factory=list)


def record_world_state(world: "World", history: WorldHistory) -> None:
    """
    Record the current world state as snapshots for all agents.
    
    Iterates over all agents in the world and appends an AgentSnapshot
    for each agent with the current month and all state fields.
    
    This function is in-memory only; persistence is not implemented yet.
    
    Args:
        world: The world state to record
        history: The WorldHistory object to append snapshots to
    """
    for agent in world.agents:
        snapshot = AgentSnapshot(
            month=world.current_month,
            label=agent.label,
            name=agent.name,
            physical=agent.physical,
            love=agent.love,
            career=agent.career,
            social=agent.social,
            intelligence=agent.intelligence,
            energy=agent.energy,
            trauma_level=agent.trauma_level,
        )
        history.snapshots.append(snapshot)

