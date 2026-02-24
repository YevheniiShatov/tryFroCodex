from datetime import datetime, timezone

from core.types import MemoryRecord, MemorySource, RetrievedMemory
from persona.evolution import PersonaEvolver
from persona.models import EvolutionParameters, Passport, PersonaState


def test_evolution_updates_trust_and_energy() -> None:
    passport = Passport(
        name="A",
        persona_description="d",
        behavioral_rules=[],
        location_region="x",
        goals=[],
        personality_traits={},
        memory_weights={},
        evolution_parameters=EvolutionParameters(0.2, 0.1, 0.05, 0.03),
    )
    evolver = PersonaEvolver(passport)
    state = PersonaState(mood=0.5, energy_level=1.0)

    memory = RetrievedMemory(
        memory=MemoryRecord(
            id="1",
            embedding=[],
            raw_text="good",
            timestamp=datetime.now(timezone.utc),
            importance_score=0.7,
            emotional_weight=0.6,
            source=MemorySource.CHAT,
            related_entities=["music"],
            decay_coefficient=1,
        ),
        semantic_similarity=0.8,
        recency_factor=1,
        relationship_relevance=1,
        score=0.8,
    )

    out = evolver.apply_interaction(state, "u1", sentiment_score=0.8, retrieved=[memory])
    assert out.trust_levels["u1"] > 0.5
    assert out.energy_level == 0.95
