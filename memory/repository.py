from __future__ import annotations

from typing import Protocol

from core.types import MemoryRecord, RetrievedMemory


class MemoryRepository(Protocol):
    async def add_memory(self, record: MemoryRecord) -> None: ...

    async def search(self, query_embedding: list[float], *, user_id: str | None, limit: int = 8) -> list[RetrievedMemory]: ...

    async def consolidate(self) -> int: ...
