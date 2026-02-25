from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from core.types import AssistantReply, MemoryRecord, MemorySource, UserMessage
from memory.repository import MemoryRepository
from persona.evolution import PersonaEvolver
from persona.models import Passport, PersonaState
from persona.prompt_builder import build_system_prompt
from providers.base import LLMProvider


class AssistantEngine:
    def __init__(
        self,
        passport: Passport,
        provider: LLMProvider,
        memory_repo: MemoryRepository,
        persona_state: PersonaState,
    ) -> None:
        self.passport = passport
        self.provider = provider
        self.memory_repo = memory_repo
        self.persona_state = persona_state
        self.evolver = PersonaEvolver(passport)

    async def handle_message(self, message: UserMessage) -> AssistantReply:
        query_embedding = await self.provider.create_embedding(message.text)
        retrieved = await self.memory_repo.search(query_embedding, user_id=message.user_id)

        system_prompt = build_system_prompt(self.passport, self.persona_state)
        context = [m.memory.raw_text for m in retrieved]
        response = await self.provider.generate_response(
            system_prompt=system_prompt,
            user_prompt=message.text,
            context=context,
        )

        # Store user message and assistant response as memories for continuity.
        await self.memory_repo.add_memory(
            MemoryRecord(
                id=f"chat-{uuid4()}",
                embedding=query_embedding,
                raw_text=message.text,
                timestamp=message.timestamp,
                importance_score=0.6,
                emotional_weight=self._sentiment(message.text),
                source=MemorySource.CHAT,
                related_entities=[message.user_id],
                decay_coefficient=0.995,
            )
        )

        reply_embedding = await self.provider.create_embedding(response)
        await self.memory_repo.add_memory(
            MemoryRecord(
                id=f"assistant-{uuid4()}",
                embedding=reply_embedding,
                raw_text=response,
                timestamp=datetime.now(timezone.utc),
                importance_score=0.5,
                emotional_weight=0.0,
                source=MemorySource.SYSTEM,
                related_entities=[message.user_id],
                decay_coefficient=0.992,
            )
        )

        self.persona_state = self.evolver.apply_interaction(
            state=self.persona_state,
            user_id=message.user_id,
            sentiment_score=self._sentiment(message.text),
            retrieved=retrieved,
        )

        return AssistantReply(
            text=response,
            retrieved_memory_ids=[m.memory.id for m in retrieved],
            persona_state_snapshot=self.persona_state.serialize(),
        )

    @staticmethod
    def _sentiment(text: str) -> float:
        lowered = text.lower()
        positive = ["thanks", "great", "love", "good", "awesome"]
        negative = ["bad", "hate", "angry", "terrible", "upset"]
        score = sum(term in lowered for term in positive) - sum(term in lowered for term in negative)
        return max(-1.0, min(1.0, score / 3))
