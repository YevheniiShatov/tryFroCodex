from __future__ import annotations

from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from core.engine import AssistantEngine
from core.types import UserMessage


class TelegramAssistantBot:
    def __init__(self, token: str, engine: AssistantEngine, simulate_typing: bool = True) -> None:
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.engine = engine
        self.simulate_typing = simulate_typing

        @self.dp.message(F.text)
        async def handle_text(message: Message) -> None:
            user_id = str(message.from_user.id) if message.from_user else "unknown"
            if self.simulate_typing:
                await self.bot.send_chat_action(message.chat.id, "typing")

            reply = await self.engine.handle_message(
                UserMessage(
                    user_id=user_id,
                    text=message.text or "",
                    timestamp=datetime.now(timezone.utc),
                )
            )
            await message.answer(reply.text)

    async def run(self) -> None:
        await self.dp.start_polling(self.bot)
