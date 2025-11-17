"""
Intro module for Agent flavor text and starting intentions.

Provides helper utilities for generating soul notes, personality summaries,
initial goal tendencies, and destiny seeds based on archetype traits.
"""

from __future__ import annotations

from typing import List

from parushini.agents.archetypes import Archetype


def generate_soul_note(archetype: Archetype) -> str:
    """
    Craft a poetic soul note that captures the essence of an archetype.

    The description leans on the highest trait clusters to convey mood.
    """
    traits = {
        "curiosity": archetype.curiosity,
        "warmth": archetype.warmth,
        "drive": archetype.drive,
        "stability": archetype.stability,
        "creativity": archetype.creativity,
        "sociability": archetype.sociability,
    }
    dominant_trait = max(traits, key=traits.get)
    tone_map = {
        "curiosity": "restless winds that chase every question",
        "warmth": "ember-soft light that heals cold rooms",
        "drive": "focused lightning chasing distant summits",
        "stability": "quiet stone that anchors trembling ground",
        "creativity": "kaleidoscopes that bloom inside the mind",
        "sociability": "crowd-surfing laughter threaded with care",
    }
    tone = tone_map.get(dominant_trait, "mysterious chords humming beneath the skin")
    return f"{archetype.name} carries {tone}."


def generate_personality_summary(archetype: Archetype) -> str:
    """
    Produce a concise personality summary grounded in trait balances.
    """
    pillars = []
    if archetype.drive >= 7:
        pillars.append("ambitious")
    if archetype.warmth >= 7:
        pillars.append("empathetic")
    if archetype.curiosity >= 7:
        pillars.append("inquisitive")
    if archetype.stability >= 7:
        pillars.append("steady")
    if archetype.creativity >= 7:
        pillars.append("imaginative")
    if archetype.sociability >= 7:
        pillars.append("gregarious")
    if not pillars:
        pillars.append("balanced")
    tone = ", ".join(pillars[:-1]) + f", and {pillars[-1]}" if len(pillars) > 1 else pillars[0]
    return f"{archetype.name} is {tone}, guided by {describe_orientation(archetype)}."


def describe_orientation(archetype: Archetype) -> str:
    """Helper to describe love vs career orientation."""
    if archetype.love_orientation > archetype.drive:
        return "heart-forward instincts"
    if archetype.drive > archetype.love_orientation:
        return "relentless purpose"
    return "an equal pull toward love and ambition"


def derive_initial_goals(archetype: Archetype) -> List[str]:
    """
    Infer initial goal domains (love, career, social, learning, rest, physical).
    """
    domains = {
        "love": archetype.love_orientation,
        "career": archetype.drive,
        "social": archetype.sociability,
        "learning": archetype.curiosity,
        "physical": (archetype.stability + archetype.hardworking) / 2,
        "rest": 10 - archetype.impulse,
    }
    sorted_domains = sorted(domains.items(), key=lambda item: item[1], reverse=True)
    return [domain for domain, _ in sorted_domains[:3]]


def generate_destiny_seed(archetype: Archetype) -> float:
    """
    Compute a deterministic destiny seed in [0, 1] using trait averages.
    """
    raw = (
        archetype.curiosity
        + archetype.creativity
        + archetype.love_orientation
        + archetype.memory_depth
    ) / 40.0
    # fold in stability to avoid extremes
    seed = min(1.0, max(0.0, raw * (0.6 + archetype.stability / 20.0)))
    return seed


