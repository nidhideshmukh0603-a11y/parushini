"""
Archetypes module.

This module defines archetypal personality templates that agents can embody.
Each archetype represents a distinct combination of trait values that influence
agent behavior, desires, and interactions.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Archetype:
    """
    Represents an archetypal personality template.
    
    Attributes:
        name: Full name of the archetype (e.g., "Vayu")
        label: Short identifier (e.g., "vayu")
        love_orientation: Orientation towards love and relationships (0-10)
        drive: Level of motivation and ambition (0-10)
        sociability: Tendency to seek social interaction (0-10)
        stability: Emotional and behavioral consistency (0-10)
        curiosity: Desire to explore and learn (0-10)
        creativity: Tendency towards creative expression (0-10)
        hardworking: Work ethic and persistence (0-10)
        intelligence_base: Base cognitive capability (0-10)
        warmth: Emotional warmth and empathy (0-10)
        impulse: Tendency towards impulsive actions (0-10)
        trauma_sensitivity: Sensitivity to negative experiences (0-10)
        memory_depth: Depth and persistence of memories (0-10)
    """
    name: str
    label: str
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


def get_default_archetypes() -> List[Archetype]:
    """
    Returns a list of the 10 default archetypes for the Parushini simulation.
    
    Returns:
        List of Archetype instances representing Vayu, Agni, Dhara, Jvala,
        Neer, Kash, Vrishti, Pashan, Ahnil, and Prith.
    """
    return [
        Archetype(
            name="Vayu",
            label="vayu",
            love_orientation=7.0,
            drive=8.0,
            sociability=6.0,
            stability=4.0,
            curiosity=9.0,
            creativity=7.0,
            hardworking=5.0,
            intelligence_base=7.0,
            warmth=6.0,
            impulse=8.0,
            trauma_sensitivity=5.0,
            memory_depth=5.0,
        ),
        Archetype(
            name="Agni",
            label="agni",
            love_orientation=6.0,
            drive=9.0,
            sociability=7.0,
            stability=5.0,
            curiosity=7.0,
            creativity=8.0,
            hardworking=8.0,
            intelligence_base=7.0,
            warmth=5.0,
            impulse=7.0,
            trauma_sensitivity=6.0,
            memory_depth=6.0,
        ),
        Archetype(
            name="Dhara",
            label="dhara",
            love_orientation=8.0,
            drive=6.0,
            sociability=8.0,
            stability=7.0,
            curiosity=5.0,
            creativity=6.0,
            hardworking=7.0,
            intelligence_base=6.0,
            warmth=8.0,
            impulse=4.0,
            trauma_sensitivity=7.0,
            memory_depth=8.0,
        ),
        Archetype(
            name="Jvala",
            label="jvala",
            love_orientation=5.0,
            drive=9.0,
            sociability=5.0,
            stability=3.0,
            curiosity=8.0,
            creativity=9.0,
            hardworking=6.0,
            intelligence_base=8.0,
            warmth=4.0,
            impulse=9.0,
            trauma_sensitivity=4.0,
            memory_depth=4.0,
        ),
        Archetype(
            name="Neer",
            label="neer",
            love_orientation=9.0,
            drive=5.0,
            sociability=7.0,
            stability=8.0,
            curiosity=6.0,
            creativity=7.0,
            hardworking=6.0,
            intelligence_base=7.0,
            warmth=9.0,
            impulse=3.0,
            trauma_sensitivity=8.0,
            memory_depth=9.0,
        ),
        Archetype(
            name="Kash",
            label="kash",
            love_orientation=4.0,
            drive=7.0,
            sociability=4.0,
            stability=6.0,
            curiosity=7.0,
            creativity=5.0,
            hardworking=8.0,
            intelligence_base=8.0,
            warmth=3.0,
            impulse=5.0,
            trauma_sensitivity=5.0,
            memory_depth=7.0,
        ),
        Archetype(
            name="Vrishti",
            label="vrishti",
            love_orientation=7.0,
            drive=6.0,
            sociability=9.0,
            stability=6.0,
            curiosity=8.0,
            creativity=8.0,
            hardworking=5.0,
            intelligence_base=6.0,
            warmth=8.0,
            impulse=6.0,
            trauma_sensitivity=7.0,
            memory_depth=6.0,
        ),
        Archetype(
            name="Pashan",
            label="pashan",
            love_orientation=5.0,
            drive=5.0,
            sociability=3.0,
            stability=9.0,
            curiosity=4.0,
            creativity=4.0,
            hardworking=9.0,
            intelligence_base=6.0,
            warmth=4.0,
            impulse=2.0,
            trauma_sensitivity=3.0,
            memory_depth=9.0,
        ),
        Archetype(
            name="Ahnil",
            label="ahnil",
            love_orientation=6.0,
            drive=8.0,
            sociability=6.0,
            stability=7.0,
            curiosity=6.0,
            creativity=6.0,
            hardworking=7.0,
            intelligence_base=8.0,
            warmth=6.0,
            impulse=5.0,
            trauma_sensitivity=6.0,
            memory_depth=7.0,
        ),
        Archetype(
            name="Prith",
            label="prith",
            love_orientation=8.0,
            drive=7.0,
            sociability=8.0,
            stability=8.0,
            curiosity=5.0,
            creativity=5.0,
            hardworking=8.0,
            intelligence_base=7.0,
            warmth=9.0,
            impulse=3.0,
            trauma_sensitivity=8.0,
            memory_depth=8.0,
        ),
    ]

