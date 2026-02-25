from __future__ import annotations

from collections import defaultdict
from statistics import fmean

from core.types import EventItem, RetrievedMemory
from persona.models import Passport, PersonaState


class PersonaEvolver:
    """Deterministic, explainable state updates based on interactions, memories, and events."""

    def __init__(self, passport: Passport) -> None:
        self.passport = passport

    def apply_interaction(
        self,
        state: PersonaState,
        user_id: str,
        sentiment_score: float,
        retrieved: list[RetrievedMemory],
    ) -> PersonaState:
        params = self.passport.evolution_parameters
        rel = state.trust_levels.get(user_id, 0.5)
        state.trust_levels[user_id] = min(1.0, rel + params.trust_interaction_boost * max(0.0, sentiment_score))

        if retrieved:
            avg_emotion = fmean(m.memory.emotional_weight for m in retrieved)
            state.mood = self._clamp(state.mood + avg_emotion * 0.1 + sentiment_score * 0.2)

            entity_scores: dict[str, float] = defaultdict(float)
            for memory in retrieved:
                for entity in memory.memory.related_entities:
                    entity_scores[entity] += memory.score
            for entity, score in entity_scores.items():
                state.interests[entity] = self._clamp(state.interests.get(entity, 0.2) + score * 0.05)

        state.energy_level = self._clamp(state.energy_level - params.energy_decay_per_turn)
        return state

    def apply_events(self, state: PersonaState, events: list[EventItem], avg_event_sentiment: float) -> PersonaState:
        params = self.passport.evolution_parameters
        if not events:
            return state
        event_scale = min(1.0, len(events) / 10)
        state.mood = self._clamp(state.mood + avg_event_sentiment * params.mood_event_impact * event_scale)
        state.worldview_bias = self._clamp(state.worldview_bias + avg_event_sentiment * params.worldview_shift_factor)
        return state

    @staticmethod
    def _clamp(value: float, min_v: float = 0.0, max_v: float = 1.0) -> float:
        return max(min_v, min(max_v, value))
