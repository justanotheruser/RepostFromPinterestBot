from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from telegram_logger import TelegramLoggerHandler


class AddTelegramLoggerHandlerMiddleware(BaseMiddleware):
    def __init__(self, telegram_logging_handler: TelegramLoggerHandler):
        self.telegram_logging_handler = telegram_logging_handler
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        data["telegram_logger_handler"] = self.telegram_logging_handler
        return await handler(event, data)
