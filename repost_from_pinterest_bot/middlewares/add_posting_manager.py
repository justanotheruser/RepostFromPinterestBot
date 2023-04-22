from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from posting_manager import PostingManager


class AddPostingManagerMiddleware(BaseMiddleware):
    def __init__(self, posting_manager: PostingManager):
        self.posting_manager = posting_manager
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        data["posting_manager"] = self.posting_manager
        return await handler(event, data)
