"""User-facing AI provider error messages.

These messages are generic and used when the downstream model provider
returns an error that should be shown (in a safe form) to Telegram users.
"""

PROVIDER_RATE_LIMIT_MESSAGE = (
    "The AI service is receiving too many requests right now. Please wait a minute and try again."
)
PROVIDER_UNAVAILABLE_MESSAGE = (
    "The AI service is temporarily overloaded or unavailable. Please try again shortly."
)
PROVIDER_TIMEOUT_MESSAGE = (
    "The AI service took too long to answer. Try a shorter message or try again shortly."
)
PROVIDER_CONFIGURATION_MESSAGE = (
    "I cannot reach the AI service because the bot configuration or request is invalid. Please try again later."
)
PROVIDER_UNEXPECTED_MESSAGE = "The AI service returned an unexpected error. Please try again later."


class GeminiUserFacingError(Exception):
    """Raised when the AI provider returns a user-facing error message."""

    def __init__(
        self,
        user_message: str,
        code: int | None = None,
        status: str | None = None,
        provider_message: str | None = None,
    ):
        self.user_message = user_message
        self.code = code
        self.status = status
        self.provider_message = provider_message
        super().__init__(user_message)


def get_gemini_user_message(code: int | None) -> str:
    if code == 429:
        return PROVIDER_RATE_LIMIT_MESSAGE

    if code in {500, 503}:
        return PROVIDER_UNAVAILABLE_MESSAGE

    if code == 504:
        return PROVIDER_TIMEOUT_MESSAGE

    if code in {400, 403, 404}:
        return PROVIDER_CONFIGURATION_MESSAGE

    return PROVIDER_UNEXPECTED_MESSAGE
