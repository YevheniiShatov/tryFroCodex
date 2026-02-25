from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from core.types import EventItem, MemoryRecord, MemorySource
from memory.repository import MemoryRepository
from providers.base import LLMProvider


class EventProcessor:
    def __init__(self, provider: LLMProvider, memory_repo: MemoryRepository) -> None:
        self.provider = provider
        self.memory_repo = memory_repo

    async def process_events(self, events: list[EventItem]) -> tuple[list[MemoryRecord], float]:
        sentiment_sum = 0.0
        created: list[MemoryRecord] = []

        for event in events:
            summary = await self.provider.summarize_memory(f"{event.title}\n{event.description}")
            embedding = await self.provider.create_embedding(summary)
            sentiment = self._heuristic_sentiment(summary)
            sentiment_sum += sentiment
            memory = MemoryRecord(
                id=f"event-{uuid4()}",
                embedding=embedding,
                raw_text=summary,
                timestamp=event.occurred_at if event.occurred_at else datetime.now(timezone.utc),
                importance_score=0.7,
                emotional_weight=sentiment,
                source=MemorySource.EVENT,
                related_entities=[event.region, event.metadata.get("source", "unknown")],
                decay_coefficient=0.98,
            )
            await self.memory_repo.add_memory(memory)
            created.append(memory)

        avg_sentiment = sentiment_sum / len(events) if events else 0.0
        return created, avg_sentiment

    @staticmethod
    def _heuristic_sentiment(text: str) -> float:
        lowered = text.lower()
        positive_terms = ["growth", "agreement", "breakthrough", "improve", "recovery"]
        negative_terms = ["conflict", "crisis", "decline", "outage", "disaster"]
        score = sum(term in lowered for term in positive_terms) - sum(term in lowered for term in negative_terms)
        return max(-1.0, min(1.0, score / 3))
