"""
Core simulator module.

This module contains the main simulation engine that orchestrates
agent interactions, event processing, and state updates.
"""

import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Dict, List, Optional

from parushini.agents.agent import Agent
from parushini.agents.archetypes import get_default_archetypes
from parushini.logic.actions import PlannedAction, apply_solo_action_effects
from parushini.logic.decisions import assign_action_targets, plan_agent_actions
from parushini.logic.desires import update_agent_desires
from parushini.logic.destiny import get_destiny_bias, set_destiny_strength
from parushini.logic.diary import generate_monthly_diary
from parushini.logic.interactions import (
    apply_interaction_outcomes,
    collect_interaction_proposals,
    evaluate_interaction_proposals,
)
from parushini.history.events_feed import EventsFeed
from parushini.history.recorder import WorldHistory, record_world_state


@dataclass
class AgentOverride:
    """Holds manual adjustments requested from the UI."""

    trauma_increase: float = 0.0
    desire_boost_domain: Optional[str] = None
    desire_boost_value: float = 0.0
    bless: bool = False
    lock_choice: bool = False
    lock_domain: Optional[str] = None


@dataclass
class World:
    """
    Represents the world state for the Parushini simulation.
    
    The World contains all agents, tracks time progression, and manages
    global themes that influence the simulation.
    """
    agents: List[Agent] = field(default_factory=list)
    current_month: int = 0
    total_months: int = 60
    global_themes: List[str] = field(default_factory=list)
    destiny_strength: float = 50.0
    agent_overrides: Dict[str, AgentOverride] = field(default_factory=dict)
    events_feed: EventsFeed = field(default_factory=EventsFeed)
    
    def initialize_default_world(self) -> None:
        """
        Initialize the world with default settings:
        - Builds 10 Agents from the default archetypes
        - Sets current_month = 0
        - Sets total_months = 12 (1 year for faster testing)
        - Initializes a simple rotating list of themes
        """
        # Create agents from default archetypes
        archetypes = get_default_archetypes()
        self.agents = [Agent.from_archetype(arch) for arch in archetypes]
        
        # Initialize time
        self.current_month = 0
        self.total_months = 12  # Temporarily set to 12 months for faster testing
        self.events_feed = EventsFeed()
        self.agent_overrides = {}
        
        # Initialize themes with a simple rotating list
        self.global_themes = [
            "ROMANCE",
            "CAREER",
            "CHAOS",
            "SELF_HELP",
            "SCIENCE",
        ]
    
    def advance_month(self) -> Optional[str]:
        """
        Advance the simulation by one month.
        
        Returns:
            The theme for the current month, or None if simulation has ended
        """
        if self.current_month >= self.total_months:
            return None
        
        self.current_month += 1
        
        # Return the theme for this month (rotating through themes)
        if self.global_themes:
            theme_index = (self.current_month - 1) % len(self.global_themes)
            return self.global_themes[theme_index]
        
        return None


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def run_month(world: World) -> None:
    """
    Run one simulation month, orchestrating all logic modules.
    
    This function:
    1. Advances the month and gets the global theme
    2. Updates desires for all agents based on the theme
    3. Plans actions for all agents
    4. Assigns targets to actions that need them
    5. Collects and evaluates interaction proposals
    6. Applies interaction outcomes
    7. Applies solo action effects
    
    The function is side-effectful and modifies world.agents directly.
    Events and trait drift are skipped for now (to be implemented later).
    
    Args:
        world: The world state to simulate
    """
    # Step 1: Advance month and get theme
    global_theme = world.advance_month()
    if global_theme is None:
        return  # Simulation has ended
    
    month_index = world.current_month
    agent_interaction_log: DefaultDict[str, List[str]] = defaultdict(list)
    
    # Step 2: Apply overrides and update desires
    pending_boosts: Dict[str, tuple[str, float]] = {}
    for agent in world.agents:
        override = world.agent_overrides.get(agent.label)
        agent.destiny_blessing = 0.2 if override and override.bless else 0.0
        agent.locked_action_domain = (
            override.lock_domain if override and override.lock_choice else None
        )
        if override and override.trauma_increase:
            agent.trauma_level = clamp(agent.trauma_level + override.trauma_increase)
            world.events_feed.add_event(
                month_index,
                f"{agent.name} carries extra trauma (+{override.trauma_increase:.0f}).",
            )
        if override and override.desire_boost_domain:
            pending_boosts[agent.label] = (
                override.desire_boost_domain,
                override.desire_boost_value,
            )
        update_agent_desires(agent, global_theme)
        if agent.label in pending_boosts:
            domain, amount = pending_boosts[agent.label]
            attr = f"desire_{domain}"
            if hasattr(agent, attr):
                setattr(agent, attr, clamp(getattr(agent, attr) + amount))
    
    # Step 3: Plan actions for all agents and collect them
    all_actions: List[PlannedAction] = []
    agent_actions_map: dict[str, List[PlannedAction]] = {}
    
    for agent in world.agents:
        actions = plan_agent_actions(agent, world)
        actions = assign_action_targets(agent, world, actions)
        all_actions.extend(actions)
        agent_actions_map[agent.label] = actions
    
    # Step 4: Handle interactions
    proposals = collect_interaction_proposals(world, all_actions)
    resolved = evaluate_interaction_proposals(world, proposals)
    apply_interaction_outcomes(world, resolved, world.events_feed, agent_interaction_log)
    
    # Step 5: Apply solo action effects for each agent
    for agent in world.agents:
        agent_actions = agent_actions_map.get(agent.label, [])
        apply_solo_action_effects(agent, agent_actions)
        # Destiny-driven spontaneous events
        if random.random() < get_destiny_bias(agent) / 4.0:
            world.events_feed.add_event(
                month_index,
                f"Destiny flares around {agent.name}, hinting at a pivot.",
            )
    
    # Step 6: Generate diaries
    for agent in world.agents:
        diary_entry = generate_monthly_diary(
            agent,
            month_index,
            agent_interaction_log.get(agent.label, []),
            world.events_feed.get_month_entries(month_index),
        )
        agent.diary_log[month_index] = diary_entry


def run_full_simulation(
    world: World,
    history: Optional[WorldHistory] = None,
) -> WorldHistory:
    """
    Run the full simulation from month 0 to total_months.
    
    This function:
    1. Creates a new WorldHistory if none is provided
    2. Records the initial state (month 0)
    3. Runs each month using run_month()
    4. Records the state after each month
    5. Returns the filled WorldHistory
    
    Args:
        world: The world state to simulate (will be modified)
        history: Optional existing WorldHistory to append to
        
    Returns:
        WorldHistory with snapshots for all agents at all months
    """
    if history is None:
        history = WorldHistory()
    
    set_destiny_strength(world.destiny_strength)
    world.events_feed = EventsFeed()
    
    # Record initial state (month 0)
    record_world_state(world, history)
    
    # Run simulation month by month
    while world.current_month < world.total_months:
        run_month(world)
        record_world_state(world, history)
    
    return history

