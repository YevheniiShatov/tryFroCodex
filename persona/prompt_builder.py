from __future__ import annotations

from persona.models import Passport, PersonaState


def build_system_prompt(passport: Passport, state: PersonaState) -> str:
    """Build system prompt dynamically from passport and state (no hardcoded persona)."""
    rules = "\n".join(f"- {rule}" for rule in passport.behavioral_rules)
    goals = "\n".join(f"- {goal}" for goal in passport.goals)
    traits = ", ".join(f"{k}: {v:.2f}" for k, v in passport.personality_traits.items())
    interests = ", ".join(f"{k}: {v:.2f}" for k, v in state.interests.items()) or "none"

    return (
        f"You are {passport.name}.\n"
        f"Persona description: {passport.persona_description}\n"
        f"Region focus: {passport.location_region}\n"
        f"Goals:\n{goals}\n"
        f"Behavioral rules:\n{rules}\n"
        f"Traits: {traits}\n"
        f"Current state -> mood={state.mood:.2f}, energy={state.energy_level:.2f}, "
        f"worldview_bias={state.worldview_bias:.2f}, interests={interests}.\n"
        "Ground responses in retrieved memories and evolving relationships."
    )
