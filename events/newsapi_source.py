from __future__ import annotations

from datetime import datetime, timezone

import httpx

from core.types import EventItem


class NewsAPIEventSource:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def fetch_events(self, *, region: str, limit: int = 5) -> list[EventItem]:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": region,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(limit, 20),
            "apiKey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        events: list[EventItem] = []
        for article in data.get("articles", []):
            published = article.get("publishedAt")
            occurred_at = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else datetime.now(timezone.utc)
            events.append(
                EventItem(
                    id=article.get("url", article.get("title", "untitled")),
                    title=article.get("title", "Untitled Event"),
                    description=article.get("description") or article.get("content") or "",
                    region=region,
                    occurred_at=occurred_at,
                    source_url=article.get("url"),
                    metadata={"source": article.get("source", {}).get("name")},
                )
            )
        return events
