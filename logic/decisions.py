"""
Decisions module.

This module implements the decision-making logic that agents use
to choose actions based on their desires, traits, and current state.
"""

from typing import TYPE_CHECKING, List

from parushini.agents.agent import Agent
from parushini.logic.actions import ActionType, PlannedAction
from parushini.logic.destiny import apply_destiny_bias

if TYPE_CHECKING:
    from parushini.core.simulator import World


def plan_agent_actions(agent: Agent, world: "World") -> List[PlannedAction]:
    """
    Plan actions for an agent based on their desires and traits.
    
    Selects exactly:
    - 1 big action (from the strongest desires)
    - 2 small actions (from remaining desires, encouraging variety)
    
    The big action is chosen from the top 1-2 strongest desires.
    Small actions are chosen from remaining desires to encourage variety.
    
    Args:
        agent: The agent to plan actions for
        world: The world state (for context, though not heavily used here)
        
    Returns:
        List of PlannedAction instances (1 big + 2 small)
    """
    actions: List[PlannedAction] = []
    
    # Create desire mapping for easier sorting
    desires = {
        "love": apply_destiny_bias(agent, agent.desire_love),
        "career": apply_destiny_bias(agent, agent.desire_career),
        "social": apply_destiny_bias(agent, agent.desire_social),
        "physical": apply_destiny_bias(agent, agent.desire_physical),
        "learning": apply_destiny_bias(agent, agent.desire_learning),
        "rest": apply_destiny_bias(agent, agent.desire_rest),
    }

    # Sort desires by strength
    sorted_desires = sorted(desires.items(), key=lambda x: x[1], reverse=True)
    
    # Pick big action from top desire
    top_desire = sorted_desires[0][0]
    locked_domain = getattr(agent, "locked_action_domain", None)
    if locked_domain and locked_domain in desires:
        top_desire = locked_domain
    big_action_type = _desire_to_big_action(top_desire)
    actions.append(PlannedAction(
        actor_label=agent.label,
        action_type=big_action_type,
        is_big=True,
        target_labels=None  # Targets assigned later
    ))
    
    # Pick 2 small actions from remaining desires (skip the one used for big action)
    remaining_desires = sorted_desires[1:]
    # Encourage variety: pick from different domains
    small_actions_picked = 0
    used_domains = {top_desire}
    
    for desire_name, desire_value in remaining_desires:
        if small_actions_picked >= 2:
            break
        if desire_name not in used_domains:
            small_action_type = _desire_to_small_action(desire_name)
            actions.append(PlannedAction(
                actor_label=agent.label,
                action_type=small_action_type,
                is_big=False,
                target_labels=None  # Targets assigned later
            ))
            used_domains.add(desire_name)
            small_actions_picked += 1
    
    # If we still need more small actions, pick from remaining (even if same domain)
    while small_actions_picked < 2 and len(remaining_desires) > 0:
        desire_name, _ = remaining_desires.pop(0)
        small_action_type = _desire_to_small_action(desire_name)
        actions.append(PlannedAction(
            actor_label=agent.label,
            action_type=small_action_type,
            is_big=False,
            target_labels=None
        ))
        small_actions_picked += 1
    
    return actions


def _desire_to_big_action(desire_name: str) -> ActionType:
    """Map desire name to corresponding big action type."""
    mapping = {
        "love": ActionType.DEEP_RELATIONSHIP,
        "career": ActionType.DEEP_WORK,
        "social": ActionType.BIG_SOCIAL_EVENT,
        "physical": ActionType.HEALTH_PUSH,
        "learning": ActionType.DEEP_STUDY,
        "rest": ActionType.MAJOR_REST,
    }
    return mapping.get(desire_name, ActionType.MAJOR_REST)


def _desire_to_small_action(desire_name: str) -> ActionType:
    """Map desire name to corresponding small action type."""
    mapping = {
        "love": ActionType.CASUAL_DATE,
        "career": ActionType.HOBBY,  # Light work-related activity
        "social": ActionType.LIGHT_SOCIAL,
        "physical": ActionType.LIGHT_EXERCISE,
        "learning": ActionType.CASUAL_LEARNING,
        "rest": ActionType.MINOR_REST,
    }
    return mapping.get(desire_name, ActionType.MINOR_REST)


def assign_action_targets(
    agent: Agent,
    world: "World",
    planned_actions: List[PlannedAction],
) -> List[PlannedAction]:
    """
    Assign target agents to actions that require interactions.
    
    For actions that can be social/romantic/collaborative, this function:
    - Scores each other agent as a potential target based on:
      * Memory: trust + attraction + familiarity
      * Traits: sociability, warmth, love_orientation, curiosity, stability, impulse
      * Penalties for recent negative interactions
    - Selects 1 main target for romantic/collab actions
    - Optionally selects a small group (2-3) for big social events
    
    Args:
        agent: The agent planning the actions
        world: The world state containing all agents
        planned_actions: List of planned actions to assign targets to
        
    Returns:
        Updated list of PlannedAction instances with target_labels populated
    """
    # Actions that require targets
    social_actions = {
        ActionType.DEEP_RELATIONSHIP,
        ActionType.BIG_SOCIAL_EVENT,
        ActionType.CASUAL_DATE,
        ActionType.LIGHT_SOCIAL,
    }
    
    # Get all other agents
    other_agents = [a for a in world.agents if a.label != agent.label]
    
    if not other_agents:
        return planned_actions  # No targets available
    
    for action in planned_actions:
        if action.action_type not in social_actions:
            continue  # This action doesn't need targets
        
        # Score each potential target
        target_scores = []
        for target in other_agents:
            score = _score_target_for_action(agent, target, action.action_type)
            target_scores.append((target.label, score))
        
        # Sort by score (highest first)
        target_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select targets based on action type
        if action.action_type == ActionType.BIG_SOCIAL_EVENT:
            # Big social: pick 2-3 targets
            num_targets = min(3, len(target_scores))
            action.target_labels = [label for label, _ in target_scores[:num_targets]]
        else:
            # Romantic/collab: pick 1 main target
            if target_scores:
                action.target_labels = [target_scores[0][0]]
    
    return planned_actions


def _score_target_for_action(
    agent: Agent,
    target: Agent,
    action_type: ActionType,
) -> float:
    """
    Score a potential target agent for a given action.
    
    Higher scores indicate better fit for the interaction.
    """
    # Get memory of target (or default values)
    if target.label in agent.memory:
        memory = agent.memory[target.label]
        trust = memory.trust
        attraction = memory.attraction
        familiarity = memory.familiarity
        last_result = memory.last_result
    else:
        trust = 50.0
        attraction = 50.0
        familiarity = 0.0
        last_result = None
    
    # Base score from memory
    score = trust + attraction + familiarity
    
    # Trait bonuses
    if action_type in {ActionType.DEEP_RELATIONSHIP, ActionType.CASUAL_DATE}:
        # Romantic actions: favor warmth and love_orientation
        score += agent.warmth * 2.0
        score += agent.love_orientation * 2.0
        score += target.warmth * 1.0
    else:
        # Social actions: favor sociability
        score += agent.sociability * 2.0
        score += target.sociability * 1.0
    
    # Curiosity and stability help with all interactions
    score += agent.curiosity * 1.0
    score += agent.stability * 1.0
    
    # Penalty for recent negative results
    if last_result == "negative":
        score -= 30.0
    elif last_result == "neutral":
        score -= 10.0
    
    # Impulse adds some randomness potential (but we're not randomizing here)
    # High impulse agents are more willing to try new targets
    if familiarity < 20.0:  # Low familiarity
        score += agent.impulse * 1.0  # Impulsive agents more open to new people
    
    return score

