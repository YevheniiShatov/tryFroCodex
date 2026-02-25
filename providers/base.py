from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, *, system_prompt: str, user_prompt: str, context: list[str]) -> str:
        raise NotImplementedError

    @abstractmethod
    async def create_embedding(self, text: str) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    async def summarize_memory(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def structured_output(self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
