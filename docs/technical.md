# Technical Documentation

## 1) Memory Pipeline

1. User/event text is embedded through `LLMProvider.create_embedding`.
2. `PostgresMemoryRepository.add_memory` persists a full memory payload including source, emotional weight, and decay coefficient.
3. Retrieval executes pgvector nearest-neighbor search and computes final ranking:

`score = semantic_similarity * importance_score * recency_factor * relationship_relevance`

Where:
- `semantic_similarity = 1 - cosine_distance`
- `recency_factor = 0.5^(age_days/halflife) * decay_coefficient`
- `relationship_relevance = relationship_bonus when user_id tagged`

4. Consolidation removes canonical text duplicates and decays low-importance memories.

## 2) Event Processing Pipeline

1. `NewsAPIEventSource.fetch_events` polls region-specific news.
2. `EventProcessor.process_events` summarizes each event, computes embedding, applies deterministic sentiment heuristic, and writes event memories.
3. The processor returns average event sentiment for persona state updates.

## 3) Persona Evolution Logic

State object (`PersonaState`) fields:
- `mood`
- `interests`
- `trust_levels`
- `worldview_bias`
- `energy_level`

Deterministic updates in `PersonaEvolver`:
- Interaction updates trust based on positive sentiment and configured boost.
- Retrieved memory emotional average modifies mood.
- Repeated entities in retrieved memory increase interest scores.
- Energy decays per turn.
- Event batches modify mood and worldview with bounded clamping.

## 4) Database Schema

See `memory/schema.sql`.

`memories` columns:
- `id` (PK)
- `embedding vector(1536)` (pgvector)
- `raw_text`
- `timestamp`
- `importance_score`
- `emotional_weight`
- `source`
- `related_entities[]`
- `decay_coefficient`

Indexes:
- ivfflat cosine index for semantic retrieval
- timestamp index for recency
- GIN index for entity filtering

## 5) API Flow

1. Telegram message enters `TelegramAssistantBot`.
2. Message is passed to `AssistantEngine.handle_message`.
3. Engine embeds user text, retrieves scored memories, builds dynamic prompt from passport+state, then calls provider chat completion.
4. Engine stores user and assistant turns as memories.
5. Persona state is evolved and included in reply metadata.
6. Telegram sends final assistant response.
