from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, chat_model: str, embedding_model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.chat_model = chat_model
        self.embedding_model = embedding_model

    async def generate_response(self, *, system_prompt: str, user_prompt: str, context: list[str]) -> str:
        context_block = "\n".join(f"- {line}" for line in context)
        completion = await self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context_block}\n\nUser: {user_prompt}"},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""

    async def create_embedding(self, text: str) -> list[float]:
        result = await self.client.embeddings.create(model=self.embedding_model, input=text)
        return list(result.data[0].embedding)

    async def summarize_memory(self, text: str) -> str:
        completion = await self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": "Summarize this memory in one sentence preserving key entities."},
                {"role": "user", "content": text},
            ],
            temperature=0,
        )
        return completion.choices[0].message.content or text

    async def structured_output(self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        completion = await self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "structured_response", "schema": schema, "strict": True},
            },
            temperature=0,
        )
        return json.loads(completion.choices[0].message.content or "{}")
