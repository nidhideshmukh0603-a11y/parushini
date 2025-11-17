"""
Interactions module.

This module handles interactions between agents, including social
exchanges, relationships, and collaborative or competitive behaviors.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from parushini.agents.agent import Agent
from parushini.logic.actions import ActionType, PlannedAction
from parushini.logic.destiny import apply_destiny_bias

if TYPE_CHECKING:
    from parushini.core.simulator import World

# Note: Random seed should be set in the main entry point (app_streamlit.py)
# to ensure reproducibility across the entire simulation


@dataclass
class InteractionProposal:
    """
    Represents a proposed interaction between agents.
    
    Attributes:
        initiator_label: Label of the agent initiating the interaction
        target_labels: List of target agent labels
        action_type: Type of action being proposed
    """
    initiator_label: str
    target_labels: List[str]
    action_type: ActionType


@dataclass
class ResolvedInteraction:
    """
    Represents a resolved interaction with acceptance/rejection results.
    
    Attributes:
        initiator_label: Label of the agent who initiated
        target_labels: All target labels that were proposed
        action_type: Type of action
        accepted_targets: Labels of targets who accepted
        rejected_targets: Labels of targets who rejected
    """
    initiator_label: str
    target_labels: List[str]
    action_type: ActionType
    accepted_targets: List[str]
    rejected_targets: List[str]


def collect_interaction_proposals(
    world: "World",
    all_actions: List[PlannedAction],
) -> List[InteractionProposal]:
    """
    Collect interaction proposals from all planned actions.
    
    Inspects all planned actions and builds InteractionProposal instances
    for actions that involve target agents (social/romantic/collaborative actions).
    
    Args:
        world: The world state
        all_actions: List of all planned actions from all agents
        
    Returns:
        List of InteractionProposal instances
    """
    proposals: List[InteractionProposal] = []
    
    # Actions that involve interactions
    interaction_actions = {
        ActionType.DEEP_RELATIONSHIP,
        ActionType.BIG_SOCIAL_EVENT,
        ActionType.CASUAL_DATE,
        ActionType.LIGHT_SOCIAL,
    }
    
    for action in all_actions:
        if action.action_type in interaction_actions and action.target_labels:
            proposals.append(InteractionProposal(
                initiator_label=action.actor_label,
                target_labels=action.target_labels.copy(),
                action_type=action.action_type,
            ))
    
    return proposals


def evaluate_interaction_proposals(
    world: "World",
    proposals: List[InteractionProposal],
) -> List[ResolvedInteraction]:
    """
    Evaluate interaction proposals and determine acceptance/rejection.
    
    For each proposal, each target agent decides whether to accept based on:
    - Their desires (love/social/rest)
    - Current energy level
    - Trauma level
    - Trust and last_result with initiator
    - Traits: stability, warmth, sociability, impulse
    
    Simple rules:
    - High desire_rest + low energy → more likely to reject
    - Matching desire domain + high trust → likely accept
    - Random variation scaled by impulse trait
    
    Args:
        world: The world state
        proposals: List of interaction proposals to evaluate
        
    Returns:
        List of ResolvedInteraction instances with acceptance results
    """
    resolved: List[ResolvedInteraction] = []
    
    for proposal in proposals:
        initiator = _get_agent_by_label(world, proposal.initiator_label)
        if not initiator:
            continue
        
        accepted_targets: List[str] = []
        rejected_targets: List[str] = []
        
        for target_label in proposal.target_labels:
            target = _get_agent_by_label(world, target_label)
            if not target:
                rejected_targets.append(target_label)
                continue
            
            # Evaluate acceptance
            if _should_accept_proposal(target, initiator, proposal.action_type):
                accepted_targets.append(target_label)
            else:
                rejected_targets.append(target_label)
        
        resolved.append(ResolvedInteraction(
            initiator_label=proposal.initiator_label,
            target_labels=proposal.target_labels.copy(),
            action_type=proposal.action_type,
            accepted_targets=accepted_targets,
            rejected_targets=rejected_targets,
        ))
    
    return resolved


def _should_accept_proposal(
    target: Agent,
    initiator: Agent,
    action_type: ActionType,
) -> bool:
    """
    Determine if a target agent should accept an interaction proposal.
    
    Returns True if accepted, False if rejected.
    """
    # Get memory of initiator (or defaults)
    if initiator.label in target.memory:
        memory = target.memory[initiator.label]
        trust = memory.trust
        last_result = memory.last_result
    else:
        trust = 50.0
        last_result = None
    
    # Base acceptance probability
    accept_prob = 0.5  # 50% base chance
    
    # Energy factor: low energy reduces acceptance
    energy_factor = target.energy / 100.0  # 0.0 to 1.0
    accept_prob *= energy_factor
    
    # Rest desire: high rest desire reduces acceptance
    rest_factor = 1.0 - (target.desire_rest / 200.0)  # Reduces by up to 50%
    accept_prob *= rest_factor
    
    # Trauma factor: high trauma reduces acceptance
    trauma_factor = 1.0 - (target.trauma_level / 200.0)  # Reduces by up to 50%
    accept_prob *= trauma_factor
    
    # Desire matching: if action matches target's desires, increase acceptance
    if action_type in {ActionType.DEEP_RELATIONSHIP, ActionType.CASUAL_DATE}:
        # Romantic actions
        desire_match = target.desire_love / 100.0
        accept_prob += desire_match * 0.3
    elif action_type in {ActionType.BIG_SOCIAL_EVENT, ActionType.LIGHT_SOCIAL}:
        # Social actions
        desire_match = target.desire_social / 100.0
        accept_prob += desire_match * 0.3
    
    # Trust factor: high trust increases acceptance
    trust_factor = trust / 100.0
    accept_prob += trust_factor * 0.2
    
    # Penalty for recent negative results
    if last_result == "negative":
        accept_prob *= 0.3  # Significant reduction
    elif last_result == "neutral":
        accept_prob *= 0.7  # Moderate reduction
    
    # Trait influences
    # Stability: more stable agents are more predictable (less variation)
    # Warmth: warmer agents more likely to accept social/romantic
    if action_type in {ActionType.DEEP_RELATIONSHIP, ActionType.CASUAL_DATE}:
        accept_prob += (target.warmth / 10.0) * 0.1
    accept_prob += (target.sociability / 10.0) * 0.1
    
    # Impulse: adds randomness (high impulse = more variation)
    impulse_variation = (target.impulse / 10.0) * 0.2  # -0.2 to +0.2
    accept_prob += random.uniform(-impulse_variation, impulse_variation)
    
    # Clamp probability
    accept_prob = max(0.0, min(1.0, accept_prob))
    
    # Make decision
    return random.random() < accept_prob


def apply_interaction_outcomes(
    world: "World",
    resolved: List[ResolvedInteraction],
    events_feed=None,
    agent_logs: Optional[dict[str, List[str]]] = None,
) -> None:
    """
    Apply outcomes of accepted interactions to agent states and memories.
    
    For each accepted interaction:
    - Computes a "chemistry" score based on trait similarity/difference
    - Updates agent states (love, career, social, trauma_level)
    - Updates agent memories (trust, attraction, familiarity, last_result, last_time)
    - Applies luck-based noise for agents with luck_enabled=True
    
    Args:
        world: The world state
        resolved: List of resolved interactions
    """
    current_time = world.current_month
    
    for interaction in resolved:
        if not interaction.accepted_targets:
            continue  # No accepted interactions
        
        initiator = _get_agent_by_label(world, interaction.initiator_label)
        if not initiator:
            continue
        
        # Process each accepted target
        for target_label in interaction.accepted_targets:
            target = _get_agent_by_label(world, target_label)
            if not target:
                continue
            
            # Compute chemistry score
            chemistry = _compute_chemistry(initiator, target, interaction.action_type)
            chemistry = apply_destiny_bias(initiator, chemistry)
            chemistry = apply_destiny_bias(target, chemistry)
            
            # Apply luck noise
            initiator_luck = random.uniform(-5.0, 5.0) if initiator.luck_enabled else 0.0
            target_luck = random.uniform(-5.0, 5.0) if target.luck_enabled else 0.0
            
            # Determine outcome quality
            if chemistry > 70.0:
                outcome_quality = "positive"
            elif chemistry < 30.0:
                outcome_quality = "negative"
            else:
                outcome_quality = "neutral"
            
            # Apply state changes based on action type
            if interaction.action_type in {ActionType.DEEP_RELATIONSHIP, ActionType.CASUAL_DATE}:
                # Romantic actions
                love_change = chemistry / 10.0 + initiator_luck
                social_change = chemistry / 15.0 + initiator_luck * 0.5
                
                initiator.love = max(0.0, min(100.0, initiator.love + love_change))
                initiator.social = max(0.0, min(100.0, initiator.social + social_change))
                
                target.love = max(0.0, min(100.0, target.love + love_change + target_luck))
                target.social = max(0.0, min(100.0, target.social + social_change + target_luck * 0.5))
                
                # Trauma can increase if negative outcome
                if outcome_quality == "negative":
                    trauma_increase = (100.0 - chemistry) / 20.0
                    initiator.trauma_level = max(0.0, min(100.0, initiator.trauma_level + trauma_increase))
                    target.trauma_level = max(0.0, min(100.0, target.trauma_level + trauma_increase))
                
                # Update memories
                trust_delta = (chemistry - 50.0) / 10.0
                attraction_delta = (chemistry - 50.0) / 8.0
                familiarity_delta = 10.0
                
                initiator.update_memory_for(
                    target_label,
                    trust_delta=trust_delta,
                    attraction_delta=attraction_delta,
                    familiarity_delta=familiarity_delta,
                    interaction_type=interaction.action_type.value,
                    result=outcome_quality,
                    current_time=current_time,
                )
                
                target.update_memory_for(
                    initiator.label,
                    trust_delta=trust_delta,
                    attraction_delta=attraction_delta,
                    familiarity_delta=familiarity_delta,
                    interaction_type=interaction.action_type.value,
                    result=outcome_quality,
                    current_time=current_time,
                )
            
            elif interaction.action_type in {ActionType.BIG_SOCIAL_EVENT, ActionType.LIGHT_SOCIAL}:
                # Social actions
                social_change = chemistry / 12.0 + initiator_luck * 0.5
                
                initiator.social = max(0.0, min(100.0, initiator.social + social_change))
                target.social = max(0.0, min(100.0, target.social + social_change + target_luck * 0.5))
                
                # Small love increase if chemistry is high
                if chemistry > 60.0:
                    love_bump = (chemistry - 60.0) / 20.0
                    initiator.love = max(0.0, min(100.0, initiator.love + love_bump))
                    target.love = max(0.0, min(100.0, target.love + love_bump))
                
                # Update memories
                trust_delta = (chemistry - 50.0) / 12.0
                familiarity_delta = 8.0
                
                initiator.update_memory_for(
                    target_label,
                    trust_delta=trust_delta,
                    familiarity_delta=familiarity_delta,
                    interaction_type=interaction.action_type.value,
                    result=outcome_quality,
                    current_time=current_time,
                )
                
                target.update_memory_for(
                    initiator.label,
                    trust_delta=trust_delta,
                    familiarity_delta=familiarity_delta,
                    interaction_type=interaction.action_type.value,
                    result=outcome_quality,
                    current_time=current_time,
                )

            # Log events
            if events_feed:
                events_feed.add_event(
                    current_time,
                    f"{initiator.name} and {target.name} shared {interaction.action_type.value.replace('_', ' ').title()} ({outcome_quality}).",
                )
            if agent_logs is not None:
                agent_logs.setdefault(initiator.label, []).append(
                    f"With {target.name}: {interaction.action_type.value.title()} ({outcome_quality})"
                )
                agent_logs.setdefault(target.label, []).append(
                    f"With {initiator.name}: {interaction.action_type.value.title()} ({outcome_quality})"
                )


def _compute_chemistry(
    agent1: Agent,
    agent2: Agent,
    action_type: ActionType,
) -> float:
    """
    Compute chemistry score between two agents for a given action type.
    
    Chemistry is based on:
    - Trait similarity/difference (complementary traits can be good)
    - Current trust and familiarity
    - Action-specific trait matching
    
    Returns a score from 0-100.
    """
    # Base chemistry from existing memory
    if agent2.label in agent1.memory:
        memory = agent1.memory[agent2.label]
        base_chemistry = (memory.trust + memory.attraction + memory.familiarity) / 3.0
    else:
        base_chemistry = 50.0  # Neutral starting point
    
    # Trait compatibility
    if action_type in {ActionType.DEEP_RELATIONSHIP, ActionType.CASUAL_DATE}:
        # Romantic: warmth and love_orientation matter
        warmth_match = 100.0 - abs(agent1.warmth * 10.0 - agent2.warmth * 10.0)
        love_match = 100.0 - abs(agent1.love_orientation * 10.0 - agent2.love_orientation * 10.0)
        trait_chemistry = (warmth_match + love_match) / 2.0
    else:
        # Social: sociability matters
        sociability_match = 100.0 - abs(agent1.sociability * 10.0 - agent2.sociability * 10.0)
        trait_chemistry = sociability_match
    
    # Stability can help (more stable = more predictable interactions)
    stability_bonus = (agent1.stability + agent2.stability) / 2.0
    
    # Combine factors
    chemistry = (
        base_chemistry * 0.4 +
        trait_chemistry * 0.4 +
        stability_bonus * 0.2
    )
    
    return max(0.0, min(100.0, chemistry))


def _get_agent_by_label(world: "World", label: str) -> Optional[Agent]:
    """Helper to get an agent by label from the world."""
    for agent in world.agents:
        if agent.label == label:
            return agent
    return None

