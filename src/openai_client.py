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
        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=self._build_headers(), json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                resp = exc.response
                body = ""
                try:
                    body = resp.text
                except Exception:
                    body = str(exc)

                # If request failed due to model not available or invalid model, try a safer fallback model once
                if resp.status_code == 400 and self.model != "gpt-3.5-turbo" and "model" in body.lower():
                    fallback = "gpt-3.5-turbo"
                    payload["model"] = fallback
                    try:
                        response = await client.post(url, headers=self._build_headers(), json=payload)
                        response.raise_for_status()
                    except httpx.HTTPStatusError as exc2:
                        raise Exception(f"HTTP {exc2.response.status_code}: {exc2.response.text}") from exc2
                else:
                    raise Exception(f"HTTP {resp.status_code}: {body}") from exc

            data = response.json()

            # Support different response shapes
            choices = data.get("choices") or []
            if not choices:
                return str(data)

            choice = choices[0]
            # new-style: choice["message"]["content"]
            if isinstance(choice, dict) and "message" in choice and isinstance(choice["message"], dict):
                content = choice["message"].get("content")
                if content is not None:
                    return content

            # older-style: choice["text"]
            if isinstance(choice, dict) and "text" in choice:
                return choice["text"]

            return str(data)
