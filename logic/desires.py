"""
Desires module.

This module handles the generation and management of agent desires,
which drive decision-making and action selection in the simulation.
"""

from parushini.agents.agent import Agent


def update_agent_desires(agent: Agent, global_theme: str) -> None:
    """
    Update agent desires based on traits, state deficits, energy, trauma, and global theme.
    
    Desires are calculated using linear combinations of:
    - Traits: love_orientation, drive, sociability, curiosity, stability
    - Deficits: (100 - category_value) for love, career, social, physical, intelligence
    - Energy: low energy increases desire_rest
    - Trauma: high trauma increases desire_rest, decreases desire_love
    - Global theme: boosts relevant desires
    
    All desires are clamped to [0, 100] at the end.
    
    Args:
        agent: The agent whose desires to update
        global_theme: Current global theme (ROMANCE, CAREER, CHAOS, SELF_HELP, SCIENCE)
    """
    # Calculate deficits (how much below 100)
    love_deficit = max(0.0, 100.0 - agent.love)
    career_deficit = max(0.0, 100.0 - agent.career)
    social_deficit = max(0.0, 100.0 - agent.social)
    physical_deficit = max(0.0, 100.0 - agent.physical)
    intelligence_deficit = max(0.0, 100.0 - agent.intelligence)
    
    # Energy factor: low energy increases rest desire
    energy_factor = (100.0 - agent.energy) / 100.0  # 0.0 to 1.0
    
    # Trauma factor: high trauma increases rest, decreases love
    trauma_factor = agent.trauma_level / 100.0  # 0.0 to 1.0
    
    # Desire Love
    # Base: love_orientation trait + love deficit
    agent.desire_love = (
        agent.love_orientation * 5.0 +  # Trait contribution (0-50)
        love_deficit * 0.3 +  # Deficit contribution
        -trauma_factor * 20.0  # Trauma reduces love desire
    )
    
    # Desire Career
    # Base: drive trait + career deficit
    agent.desire_career = (
        agent.drive * 5.0 +  # Trait contribution (0-50)
        career_deficit * 0.3  # Deficit contribution
    )
    
    # Desire Social
    # Base: sociability trait + social deficit
    agent.desire_social = (
        agent.sociability * 5.0 +  # Trait contribution (0-50)
        social_deficit * 0.3  # Deficit contribution
    )
    
    # Desire Physical
    # Base: physical deficit (no specific trait, but deficit drives it)
    agent.desire_physical = (
        physical_deficit * 0.4  # Deficit contribution
    )
    
    # Desire Learning
    # Base: curiosity trait + intelligence deficit
    agent.desire_learning = (
        agent.curiosity * 5.0 +  # Trait contribution (0-50)
        intelligence_deficit * 0.3  # Deficit contribution
    )
    
    # Desire Rest
    # Base: low energy + high trauma + low stability (unstable agents need more rest)
    stability_factor = (10.0 - agent.stability) / 10.0  # Inverse stability
    agent.desire_rest = (
        energy_factor * 40.0 +  # Energy contribution (0-40)
        trauma_factor * 30.0 +  # Trauma contribution (0-30)
        stability_factor * 20.0  # Stability contribution (0-20)
    )
    
    # Apply global theme bonuses
    theme_bonus = 15.0  # Boost for matching theme
    if global_theme == "ROMANCE":
        agent.desire_love += theme_bonus
    elif global_theme == "CAREER" or global_theme == "CAREER_HUSTLE":
        agent.desire_career += theme_bonus
    elif global_theme == "CHAOS":
        # Chaos increases all desires slightly, but especially rest
        agent.desire_love += theme_bonus * 0.5
        agent.desire_career += theme_bonus * 0.5
        agent.desire_social += theme_bonus * 0.5
        agent.desire_rest += theme_bonus * 0.7
    elif global_theme == "SELF_HELP":
        agent.desire_learning += theme_bonus
        agent.desire_physical += theme_bonus
    elif global_theme == "SCIENCE" or global_theme == "CURIOSITY":
        agent.desire_learning += theme_bonus
    
    # Clamp all desires to [0, 100]
    agent.desire_love = max(0.0, min(100.0, agent.desire_love))
    agent.desire_career = max(0.0, min(100.0, agent.desire_career))
    agent.desire_social = max(0.0, min(100.0, agent.desire_social))
    agent.desire_physical = max(0.0, min(100.0, agent.desire_physical))
    agent.desire_learning = max(0.0, min(100.0, agent.desire_learning))
    agent.desire_rest = max(0.0, min(100.0, agent.desire_rest))

