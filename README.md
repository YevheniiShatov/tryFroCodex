# Evolving AI Assistant (Telegram + Persistent Memory)

Production-oriented async Python assistant with:
- Dynamic persona prompt generated from a JSON passport.
- Long-term memory in PostgreSQL + pgvector.
- Event ingestion from region-specific external feeds.
- Deterministic, explainable personality evolution.
- Telegram bot interface.

## Architecture Overview

```text
Telegram Bot (aiogram)
        |
        v
   AssistantEngine ----------------------------+
   |                                           |
   |                               PersonaEvolver (deterministic state updates)
   |
   +--> Prompt Builder (from passport + state)
   +--> LLMProvider (OpenAI by default)
   +--> MemoryRepository (Postgres + pgvector)
   |
EventSource (News API) -> EventProcessor ------+
                     writes event memories + influences persona mood/worldview
```

## Repository Structure

```text
core/       # orchestration engine + shared domain types
memory/     # repository contracts, Postgres pgvector implementation, SQL schema
events/     # event source adapters + event-to-memory processor
persona/    # passport/state models, prompt builder, evolution logic
providers/  # pluggable LLM provider interface + OpenAI implementation
telegram/   # Telegram adapter (aiogram)
config/     # settings and passport examples
docs/       # technical docs
```

## Setup

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure PostgreSQL with pgvector

```bash
psql "$POSTGRES_DSN" -f memory/schema.sql
```

### 3) Environment variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_CHAT_MODEL` | Chat model name (default: `gpt-4o-mini`) |
| `OPENAI_EMBEDDING_MODEL` | Embedding model name (default: `text-embedding-3-small`) |
| `POSTGRES_DSN` | PostgreSQL DSN |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `NEWS_API_KEY` | API key for NewsAPI |
| `PASSPORT_PATH` | Path to passport JSON (default `config/passport.example.json`) |

### 4) Run

```bash
python main.py
```

## Engineering Notes

- No hardcoded personality prompt logic: prompt is generated from `Passport` and `PersonaState`.
- Memory retrieval ranking follows required weighted formula.
- All modules are designed for dependency injection and isolated testing.
- Event memories are first-class memories with source=`event`.

See full technical details in `docs/technical.md`.
