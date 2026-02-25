CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    embedding vector(1536) NOT NULL,
    raw_text TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    importance_score DOUBLE PRECISION NOT NULL CHECK (importance_score >= 0 AND importance_score <= 1),
    emotional_weight DOUBLE PRECISION NOT NULL CHECK (emotional_weight >= -1 AND emotional_weight <= 1),
    source TEXT NOT NULL CHECK (source IN ('chat', 'event', 'system')),
    related_entities TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    decay_coefficient DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (decay_coefficient > 0)
);

CREATE INDEX IF NOT EXISTS memories_embedding_idx ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS memories_timestamp_idx ON memories (timestamp DESC);
CREATE INDEX IF NOT EXISTS memories_entities_gin_idx ON memories USING GIN (related_entities);
