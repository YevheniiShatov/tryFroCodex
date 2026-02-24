from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EvolutionParameters:
    mood_event_impact: float
    trust_interaction_boost: float
    energy_decay_per_turn: float
    worldview_shift_factor: float


@dataclass(slots=True)
class Passport:
    name: str
    persona_description: str
    behavioral_rules: list[str]
    location_region: str
    goals: list[str]
    personality_traits: dict[str, float]
    memory_weights: dict[str, float]
    evolution_parameters: EvolutionParameters

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Passport":
        return Passport(
            name=data["name"],
            persona_description=data["persona_description"],
            behavioral_rules=data["behavioral_rules"],
            location_region=data["location_region"],
            goals=data["goals"],
            personality_traits=data["personality_traits"],
            memory_weights=data["memory_weights"],
            evolution_parameters=EvolutionParameters(**data["evolution_parameters"]),
        )


@dataclass(slots=True)
class PersonaState:
    mood: float
    interests: dict[str, float] = field(default_factory=dict)
    trust_levels: dict[str, float] = field(default_factory=dict)
    worldview_bias: float = 0.0
    energy_level: float = 1.0

    def serialize(self) -> dict[str, Any]:
        return {
            "mood": self.mood,
            "interests": self.interests,
            "trust_levels": self.trust_levels,
            "worldview_bias": self.worldview_bias,
            "energy_level": self.energy_level,
        }
