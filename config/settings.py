from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from persona.models import Passport, PersonaState


@dataclass(slots=True)
class Settings:
    openai_api_key: str
    openai_chat_model: str
    openai_embedding_model: str
    postgres_dsn: str
    telegram_bot_token: str
    news_api_key: str
    passport_path: Path


def load_passport(path: Path) -> Passport:
    return Passport.from_dict(json.loads(path.read_text()))


def default_persona_state() -> PersonaState:
    return PersonaState(mood=0.5, interests={}, trust_levels={}, worldview_bias=0.5, energy_level=1.0)
