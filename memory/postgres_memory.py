from __future__ import annotations

from datetime import datetime, timezone

import asyncpg

from core.types import MemoryRecord, MemorySource, RetrievedMemory
from memory.repository import MemoryRepository


class PostgresMemoryRepository(MemoryRepository):
    def __init__(self, dsn: str, memory_weights: dict[str, float]) -> None:
        self.dsn = dsn
        self.memory_weights = memory_weights
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(self.dsn)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def add_memory(self, record: MemoryRecord) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO memories
                (id, embedding, raw_text, timestamp, importance_score, emotional_weight, source, related_entities, decay_coefficient)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                record.id,
                record.embedding,
                record.raw_text,
                record.timestamp,
                record.importance_score,
                record.emotional_weight,
                record.source.value,
                record.related_entities,
                record.decay_coefficient,
            )

    async def search(self, query_embedding: list[float], *, user_id: str | None, limit: int = 8) -> list[RetrievedMemory]:
        assert self._pool is not None
        now = datetime.now(timezone.utc)
        recency_halflife_days = self.memory_weights.get("recency_halflife_days", 7.0)
        relationship_bonus = self.memory_weights.get("relationship_bonus", 1.2)

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    id,
                    embedding,
                    raw_text,
                    timestamp,
                    importance_score,
                    emotional_weight,
                    source,
                    related_entities,
                    decay_coefficient,
                    1 - (embedding <=> $1::vector) AS semantic_similarity
                FROM memories
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                query_embedding,
                limit * 4,
            )

        ranked: list[RetrievedMemory] = []
        for row in rows:
            age_days = max(0.0, (now - row["timestamp"]).total_seconds() / 86400)
            recency_factor = pow(0.5, age_days / recency_halflife_days) * row["decay_coefficient"]
            relationship_relevance = relationship_bonus if user_id and user_id in row["related_entities"] else 1.0
            score = (
                row["semantic_similarity"]
                * row["importance_score"]
                * recency_factor
                * relationship_relevance
            )
            ranked.append(
                RetrievedMemory(
                    memory=MemoryRecord(
                        id=row["id"],
                        embedding=list(row["embedding"]),
                        raw_text=row["raw_text"],
                        timestamp=row["timestamp"],
                        importance_score=row["importance_score"],
                        emotional_weight=row["emotional_weight"],
                        source=MemorySource(row["source"]),
                        related_entities=list(row["related_entities"]),
                        decay_coefficient=row["decay_coefficient"],
                    ),
                    semantic_similarity=row["semantic_similarity"],
                    recency_factor=recency_factor,
                    relationship_relevance=relationship_relevance,
                    score=score,
                )
            )
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:limit]

    async def consolidate(self) -> int:
        """Simple deterministic consolidation by merging near-duplicate texts and decaying low-value memory."""
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            merged = await conn.execute(
                """
                WITH duplicate_groups AS (
                    SELECT min(id) keeper_id, array_agg(id) ids, regexp_replace(lower(raw_text), '\\W+', ' ', 'g') canon
                    FROM memories
                    GROUP BY canon
                    HAVING count(*) > 1
                )
                DELETE FROM memories m
                USING duplicate_groups g
                WHERE m.id = ANY(g.ids) AND m.id <> g.keeper_id
                """
            )
            await conn.execute(
                """
                UPDATE memories
                SET decay_coefficient = GREATEST(0.05, decay_coefficient - 0.03)
                WHERE importance_score < 0.35
                """
            )
        return int(merged.split()[-1])
