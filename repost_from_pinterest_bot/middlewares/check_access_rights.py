from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery


class CheckAccessRightsMiddleware(BaseMiddleware):
    def __init__(self, admins: list[int]):
        self.admins = admins
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if data['event_from_user'].id not in self.admins:
            return
        return await handler(event, data)
