from __future__ import annotations

import asyncio
import os
from pathlib import Path

from config.settings import default_persona_state, load_passport
from core.engine import AssistantEngine
from events.newsapi_source import NewsAPIEventSource
from events.processor import EventProcessor
from memory.postgres_memory import PostgresMemoryRepository
from providers.openai_provider import OpenAIProvider
from telegram.bot import TelegramAssistantBot


async def bootstrap() -> None:
    passport = load_passport(Path(os.getenv("PASSPORT_PATH", "config/passport.example.json")))
    provider = OpenAIProvider(
        api_key=os.environ["OPENAI_API_KEY"],
        chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )

    memory_repo = PostgresMemoryRepository(os.environ["POSTGRES_DSN"], passport.memory_weights)
    await memory_repo.connect()

    engine = AssistantEngine(
        passport=passport,
        provider=provider,
        memory_repo=memory_repo,
        persona_state=default_persona_state(),
    )

    # One-shot event ingestion at boot; run as a periodic task in production scheduler.
    event_source = NewsAPIEventSource(os.environ["NEWS_API_KEY"])
    events = await event_source.fetch_events(region=passport.location_region, limit=5)
    processor = EventProcessor(provider, memory_repo)
    _, avg_sentiment = await processor.process_events(events)
    engine.persona_state = engine.evolver.apply_events(engine.persona_state, events, avg_sentiment)

    tg = TelegramAssistantBot(os.environ["TELEGRAM_BOT_TOKEN"], engine)
    await tg.run()


if __name__ == "__main__":
    asyncio.run(bootstrap())
