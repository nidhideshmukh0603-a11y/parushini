"""
Actions module.

This module defines the available actions that agents can perform
and handles their execution and effects on the simulation state.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from parushini.agents.agent import Agent


class ActionType(Enum):
    """Enumeration of all available action types in the simulation."""
    # Big actions
    DEEP_WORK = "DEEP_WORK"
    DEEP_RELATIONSHIP = "DEEP_RELATIONSHIP"
    BIG_SOCIAL_EVENT = "BIG_SOCIAL_EVENT"
    DEEP_STUDY = "DEEP_STUDY"
    MAJOR_REST = "MAJOR_REST"
    HEALTH_PUSH = "HEALTH_PUSH"
    
    # Small actions
    LIGHT_SOCIAL = "LIGHT_SOCIAL"
    LIGHT_EXERCISE = "LIGHT_EXERCISE"
    CASUAL_DATE = "CASUAL_DATE"
    CASUAL_LEARNING = "CASUAL_LEARNING"
    HOBBY = "HOBBY"
    MINOR_REST = "MINOR_REST"


@dataclass
class PlannedAction:
    """
    Represents a planned action by an agent.
    
    Attributes:
        actor_label: Label of the agent performing the action
        action_type: Type of action to perform
        is_big: Whether this is a big action (True) or small action (False)
        target_labels: Optional list of target agent labels for interactions
    """
    actor_label: str
    action_type: ActionType
    is_big: bool
    target_labels: Optional[List[str]] = None


def apply_solo_action_effects(agent: Agent, actions: List[PlannedAction]) -> None:
    """
    Apply the effects of solo actions (non-interaction actions) to an agent.
    
    This function processes actions that don't require other agents and directly
    modifies the agent's state fields: physical, career, social, intelligence, energy.
    
    Design principles:
    - Big actions have larger effects than small actions
    - Actions that require effort (work, study, exercise) cost energy
    - Rest actions restore energy and provide small physical benefits
    - Career actions boost career, study actions boost intelligence
    - Social solo actions (like hobby) provide small social benefits
    
    All state changes are clamped to [0, 100] after each action.
    
    Args:
        agent: The agent whose actions to process
        actions: List of PlannedAction instances for this agent
    """
    # Solo actions are those without targets or that don't require interactions
    solo_action_types = {
        ActionType.DEEP_WORK,
        ActionType.DEEP_STUDY,
        ActionType.MAJOR_REST,
        ActionType.HEALTH_PUSH,
        ActionType.LIGHT_EXERCISE,
        ActionType.CASUAL_LEARNING,
        ActionType.HOBBY,
        ActionType.MINOR_REST,
    }
    
    for action in actions:
        # Only process solo actions (no targets or not interaction-based)
        if action.target_labels:
            continue  # Skip interaction-based actions
        
        if action.action_type not in solo_action_types:
            continue  # Skip other action types
        
        # Apply effects based on action type and size
        if action.is_big:
            _apply_big_solo_action(agent, action.action_type)
        else:
            _apply_small_solo_action(agent, action.action_type)


def _apply_big_solo_action(agent: Agent, action_type: ActionType) -> None:
    """Apply effects of a big solo action."""
    if action_type == ActionType.DEEP_WORK:
        # Big career gain, medium energy cost
        agent.career = max(0.0, min(100.0, agent.career + 15.0))
        agent.energy = max(0.0, min(100.0, agent.energy - 12.0))
    
    elif action_type == ActionType.DEEP_STUDY:
        # Intelligence gain, some career gain, energy cost
        agent.intelligence = max(0.0, min(100.0, agent.intelligence + 12.0))
        agent.career = max(0.0, min(100.0, agent.career + 5.0))
        agent.energy = max(0.0, min(100.0, agent.energy - 10.0))
    
    elif action_type == ActionType.MAJOR_REST:
        # Big energy gain, small physical gain
        agent.energy = max(0.0, min(100.0, agent.energy + 20.0))
        agent.physical = max(0.0, min(100.0, agent.physical + 3.0))
    
    elif action_type == ActionType.HEALTH_PUSH:
        # Physical gain, energy cost
        agent.physical = max(0.0, min(100.0, agent.physical + 12.0))
        agent.energy = max(0.0, min(100.0, agent.energy - 10.0))


def _apply_small_solo_action(agent: Agent, action_type: ActionType) -> None:
    """Apply effects of a small solo action."""
    if action_type == ActionType.LIGHT_EXERCISE:
        # Small physical gain, small energy cost
        agent.physical = max(0.0, min(100.0, agent.physical + 5.0))
        agent.energy = max(0.0, min(100.0, agent.energy - 4.0))
    
    elif action_type == ActionType.CASUAL_LEARNING:
        # Small intelligence gain, small energy cost
        agent.intelligence = max(0.0, min(100.0, agent.intelligence + 5.0))
        agent.energy = max(0.0, min(100.0, agent.energy - 3.0))
    
    elif action_type == ActionType.HOBBY:
        # Small social gain, small career gain, small energy cost
        agent.social = max(0.0, min(100.0, agent.social + 4.0))
        agent.career = max(0.0, min(100.0, agent.career + 2.0))
        agent.energy = max(0.0, min(100.0, agent.energy - 2.0))
    
    elif action_type == ActionType.MINOR_REST:
        # Small energy gain, tiny physical gain
        agent.energy = max(0.0, min(100.0, agent.energy + 8.0))
        agent.physical = max(0.0, min(100.0, agent.physical + 1.0))

