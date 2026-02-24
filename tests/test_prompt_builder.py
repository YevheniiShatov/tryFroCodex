from persona.models import EvolutionParameters, Passport, PersonaState
from persona.prompt_builder import build_system_prompt


def test_prompt_is_passport_driven() -> None:
    passport = Passport(
        name="Aster",
        persona_description="desc",
        behavioral_rules=["rule1"],
        location_region="Berlin",
        goals=["goal1"],
        personality_traits={"empathy": 0.9},
        memory_weights={"recency_halflife_days": 7},
        evolution_parameters=EvolutionParameters(
            mood_event_impact=0.2,
            trust_interaction_boost=0.1,
            energy_decay_per_turn=0.02,
            worldview_shift_factor=0.05,
        ),
    )
    state = PersonaState(mood=0.4)
    prompt = build_system_prompt(passport, state)

    assert "Aster" in prompt
    assert "Berlin" in prompt
    assert "rule1" in prompt
