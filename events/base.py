from __future__ import annotations

from typing import Protocol

from core.types import EventItem


class EventSource(Protocol):
    async def fetch_events(self, *, region: str, limit: int = 5) -> list[EventItem]: ...
