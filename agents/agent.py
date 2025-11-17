"""
Agent module.

This module defines the base Agent class that represents individual
entities in the simulation with their traits, state, and behaviors.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from parushini.agents.archetypes import Archetype
from parushini.agents.intro import (
    derive_initial_goals,
    generate_destiny_seed,
    generate_personality_summary,
    generate_soul_note,
)


@dataclass
class AgentMemory:
    """
    Represents memory of another agent.
    
    Attributes:
        trust: Level of trust in this agent (0-100)
        attraction: Level of attraction to this agent (0-100)
        familiarity: Level of familiarity with this agent (0-100)
        last_interaction_type: Type of last interaction, if any
        last_result: Result of last interaction, if any
        last_time: Time (month) of last interaction, if any
    """
    trust: float = 50.0
    attraction: float = 50.0
    familiarity: float = 0.0
    last_interaction_type: Optional[str] = None
    last_result: Optional[str] = None
    last_time: Optional[int] = None


@dataclass
class Agent:
    """
    Represents an agent in the Parushini simulation.
    
    An agent has identity, traits (from an archetype), state values,
    desires, memory of other agents, and configuration settings.
    """
    # Identity
    name: str
    label: str
    
    # Traits (copied from Archetype)
    love_orientation: float
    drive: float
    sociability: float
    stability: float
    curiosity: float
    creativity: float
    hardworking: float
    intelligence_base: float
    warmth: float
    impulse: float
    trauma_sensitivity: float
    memory_depth: float
    
    # Narrative identity
    soul_note: str = ""
    personality_summary: str = ""
    initial_goals: List[str] = field(default_factory=list)
    destiny_seed: float = 0.5
    destiny_blessing: float = 0.0
    locked_action_domain: Optional[str] = None

    # State (0-100 values)
    physical: float = 50.0
    love: float = 50.0
    career: float = 50.0
    social: float = 50.0
    intelligence: float = 50.0
    energy: float = 50.0
    trauma_level: float = 0.0
    
    # Desires
    desire_love: float = 0.0
    desire_career: float = 0.0
    desire_social: float = 0.0
    desire_physical: float = 0.0
    desire_learning: float = 0.0
    desire_rest: float = 0.0
    
    # Memory (Dict mapping other agent labels to AgentMemory)
    memory: Dict[str, AgentMemory] = field(default_factory=dict)
    
    # Config
    luck_enabled: bool = True
    diary_log: Dict[int, str] = field(default_factory=dict)
    last_state_snapshot: Dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def from_archetype(cls, archetype: Archetype) -> "Agent":
        """
        Factory method to create an Agent from an Archetype.
        
        Args:
            archetype: The archetype to base this agent on
            
        Returns:
            A new Agent instance with traits copied from the archetype
            and state initialized to default values
        """
        agent = cls(
            name=archetype.name,
            label=archetype.label,
            love_orientation=archetype.love_orientation,
            drive=archetype.drive,
            sociability=archetype.sociability,
            stability=archetype.stability,
            curiosity=archetype.curiosity,
            creativity=archetype.creativity,
            hardworking=archetype.hardworking,
            intelligence_base=archetype.intelligence_base,
            warmth=archetype.warmth,
            impulse=archetype.impulse,
            trauma_sensitivity=archetype.trauma_sensitivity,
            memory_depth=archetype.memory_depth,
            soul_note=generate_soul_note(archetype),
            personality_summary=generate_personality_summary(archetype),
            initial_goals=derive_initial_goals(archetype),
            destiny_seed=generate_destiny_seed(archetype),
        )
        agent.reset_state()
        return agent
    
    def reset_state(self) -> None:
        """
        Reset life categories and energy to default mid-20s baseline (50).
        Does not reset trauma_level or memory.
        """
        self.physical = 50.0
        self.love = 50.0
        self.career = 50.0
        self.social = 50.0
        self.intelligence = 50.0
        self.energy = 50.0
        self.last_state_snapshot = self._capture_state_snapshot()
    
    def update_memory_for(
        self,
        other_label: str,
        trust_delta: float = 0.0,
        attraction_delta: float = 0.0,
        familiarity_delta: float = 0.0,
        interaction_type: Optional[str] = None,
        result: Optional[str] = None,
        current_time: Optional[int] = None,
    ) -> None:
        """
        Update memory for another agent.
        
        Args:
            other_label: Label of the other agent
            trust_delta: Change in trust level
            attraction_delta: Change in attraction level
            familiarity_delta: Change in familiarity level
            interaction_type: Type of interaction that occurred
            result: Result of the interaction
            current_time: Current time (month) of the interaction
        """
        if other_label not in self.memory:
            self.memory[other_label] = AgentMemory()
        
        memory = self.memory[other_label]
        
        # Update values with bounds checking (0-100)
        memory.trust = max(0.0, min(100.0, memory.trust + trust_delta))
        memory.attraction = max(0.0, min(100.0, memory.attraction + attraction_delta))
        memory.familiarity = max(0.0, min(100.0, memory.familiarity + familiarity_delta))
        
        # Update interaction history
        if interaction_type is not None:
            memory.last_interaction_type = interaction_type
        if result is not None:
            memory.last_result = result
        if current_time is not None:
            memory.last_time = current_time

    def _capture_state_snapshot(self) -> Dict[str, float]:
        """Capture the current core state metrics."""
        return {
            "physical": self.physical,
            "love": self.love,
            "career": self.career,
            "social": self.social,
            "intelligence": self.intelligence,
            "energy": self.energy,
            "trauma_level": self.trauma_level,
        }


