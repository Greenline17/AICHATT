from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from src.bot_service import BotService
from src.chat_service import ChatService
from src.entities.base import Base
from src.gemini import Gemini
from src.routes import router
from src.services.database_service import engine
from src.services.telegram_service import TelegramService

load_dotenv()


async def create_database_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


def create_app(
    telegram_service_factory: Callable[[], TelegramService] = TelegramService,
    chat_service_factory: Callable[[], ChatService] = ChatService,
    gemini_factory: Callable[[], Gemini] = Gemini,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        telegram_service = telegram_service_factory()
        app.state.telegram_service = telegram_service
        app.state.bot_service = BotService(
            telegram_service, chat_service_factory(), gemini_factory
        )

        try:
            await create_database_tables()
            if getattr(telegram_service, "bot", None) is not None:
                try:
                    await telegram_service.set_webhook()
                except Exception as exc:  # pragma: no cover - startup best effort
                    print(f"Webhook setup skipped: {exc}")
            yield
        finally:
            telegram_service = getattr(app.state, "telegram_service", None)
            if telegram_service is not None:
                await telegram_service.close()

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
