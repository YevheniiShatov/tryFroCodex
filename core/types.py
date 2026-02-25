from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MemorySource(str, Enum):
    CHAT = "chat"
    EVENT = "event"
    SYSTEM = "system"


@dataclass(slots=True)
class MemoryRecord:
    id: str
    embedding: list[float]
    raw_text: str
    timestamp: datetime
    importance_score: float
    emotional_weight: float
    source: MemorySource
    related_entities: list[str]
    decay_coefficient: float


@dataclass(slots=True)
class RetrievedMemory:
    memory: MemoryRecord
    semantic_similarity: float
    recency_factor: float
    relationship_relevance: float
    score: float


@dataclass(slots=True)
class EventItem:
    id: str
    title: str
    description: str
    region: str
    occurred_at: datetime
    source_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UserMessage:
    user_id: str
    text: str
    timestamp: datetime


@dataclass(slots=True)
class AssistantReply:
    text: str
    retrieved_memory_ids: list[str]
    persona_state_snapshot: dict[str, Any]
