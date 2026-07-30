from io import BytesIO
from os import getenv
from urllib.parse import urljoin

from telegram import Message, Update
from telegram.ext import ApplicationBuilder
from PIL import Image


def resolve_webhook_url(path: str = "/webhook") -> str:
    explicit_url = getenv("WEBHOOK_URL")
    if explicit_url:
        if explicit_url.startswith("http://") or explicit_url.startswith("https://"):
            if explicit_url.endswith("/webhook"):
                return explicit_url
            return explicit_url.rstrip("/") + "/" + path.lstrip("/")
        return explicit_url

    railway_domain = getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_domain:
        return f"https://{railway_domain}/{path.lstrip('/')}"

    port = getenv("PORT", "8000")
    return f"http://127.0.0.1:{port}/{path.lstrip('/')}"


class TelegramService:
    def __init__(self):
        self._telegram_bot = ApplicationBuilder().token(getenv("TELEGRAM_BOT_TOKEN")).build().bot

    @property
    def bot(self):
        return self._telegram_bot

    def build_update(self, payload: dict) -> Update:
        return Update.de_json(payload, self.bot)

    def is_secure_webhook_enabled(self) -> bool:
        """Check if secure webhook is enabled.

        Returns:
            True if secure webhook is enabled, False otherwise.
        """
        return getenv("ENABLE_SECURE_WEBHOOK_TOKEN", "True").lower() == "true"
    
    def get_secure_webhook_token(self) -> str:
        """Get the secure webhook token from environment variable.

        Returns:
            The secure webhook token as a string.
        """
        return getenv("TELEGRAM_WEBHOOK_SECRET")
    
    def is_secure_webhook_token_valid(self, headers_token: str) -> bool:
        """Validate the secure webhook token from headers.

        Args:
            headers_token: The token from the request headers.

        Returns:
            True if the token is valid, False otherwise.
        """
        secret_token = self.get_secure_webhook_token()
        return bool(secret_token) and headers_token == secret_token
    
    async def send_start_message(self, chat_id: int):
        """Send the start message to the user.

        Args:
            chat_id: The chat ID to send the message to.
        """
        await self.send_message(chat_id=chat_id, text="Welcome to Gemini Bot. Send me a message or an image to get started.")

    async def send_unauthorized_message(self, chat_id: int):
        """Send an unauthorized access message to the user.

        Args:
            chat_id: The chat ID to send the message to.
        """
        await self.send_message(chat_id=chat_id, text="You are not authorized to access this service.")

    async def send_new_chat_message(self, chat_id: int):
        """Send a new chat started message to the user.

        Args:
            chat_id: The chat ID to send the message to.
        """
        await self.send_message(chat_id=chat_id, text="New chat started. How can I assist you?")

    
    async def send_message(self, chat_id: int, text: str) -> Message:
        """Send a message to the user.

        Args:
            chat_id: The chat ID to send the message to.
            text: The message text content.
        """
        return await self.bot.send_message(chat_id=chat_id, text=text)
    
    async def update_message(self, chat_id: int, message_id: int, text: str) -> Message:
        """Update a message for the user.

        Args:
            chat_id: The chat ID to update the message for.
            message_id: The message ID to update.
            text: The new message text content.
        """
        return await self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)
    
    async def get_image_from_message(self, message: Message) -> Image.Image | None:
        """Retrieve the image file bytes from a Telegram message.

        Args:
            message: The Telegram message object.
        Returns:
            The image file bytes if available, None otherwise.
        """

        if message.photo:
            file_id = message.photo[-1].file_id
            file = await self.bot.get_file(file_id)
            bytes_array = await file.download_as_bytearray()
            bytesIO = BytesIO(bytes_array)
            image = Image.open(bytesIO)
            return image
        return None

    async def set_webhook(self) -> None:
        """Set Telegram webhook to the current public URL."""
        webhook_url = resolve_webhook_url()
        if self.is_secure_webhook_enabled():
            secret_token = self.get_secure_webhook_token()
            if secret_token:
                await self.bot.set_webhook(url=webhook_url, secret_token=secret_token)
                return
            print("Secure webhook enabled but TELEGRAM_WEBHOOK_SECRET is not set.")

        await self.bot.set_webhook(url=webhook_url)

    async def close(self) -> None:
        """Close the underlying Telegram bot client if supported."""
        shutdown = getattr(self.bot, "shutdown", None)
        if shutdown is not None:
            await shutdown()
