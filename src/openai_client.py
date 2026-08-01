from __future__ import annotations

import os
from typing import Any

import httpx


class OpenAIClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_request_payload(self, prompt: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        messages = []
        for item in history or []:
            role = item.get("role", "user")
            parts = item.get("parts", [])
            text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
            messages.append({"role": role, "content": text})
        messages.append({"role": "user", "content": prompt})
        return {"model": self.model, "messages": messages}

    async def complete(self, prompt: str, history: list[dict[str, Any]] | None = None) -> str:
        payload = self._build_request_payload(prompt, history)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._build_headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
