from os import getenv

from .config import Config
from .exceptions.gemini_exceptions import GeminiUserFacingError, get_gemini_user_message
from .openai_client import OpenAIClient


class Gemini:
    """Compatibility wrapper around OpenAI Chat Completions API."""

    def __init__(self):
        self._client = OpenAIClient(
            api_key=getenv("OPENAI_API_KEY") or getenv("GEMINI_API_KEY"),
            model=getenv("OPENAI_MODEL", Config.DEFAULT_GEMINI_MODEL_NAME),
        )

    def get_chat(self, history: list) -> object:
        return history

    async def send_message(self, prompt: str, chat: object) -> str:
        try:
            history = chat if isinstance(chat, list) else []
            return await self._client.complete(prompt, history=history)
        except Exception as exc:  # pragma: no cover - compatibility path
            code = getattr(exc, "response", None)
            status = None
            message = str(exc)
            if code is not None:
                status = getattr(code, "status_code", None)
                code = getattr(code, "status_code", None)
            raise GeminiUserFacingError(
                get_gemini_user_message(code),
                code=code,
                status=status,
                provider_message=message,
            ) from exc

    @staticmethod
    async def send_image(prompt: str, image: object, chat: object) -> str:
        return "Image processing is not available for the OpenAI chat path yet."

    async def close(self) -> None:
        return None

    async def __aenter__(self) -> "Gemini":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
