import asyncio
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery

from config_reader import config
from handlers import start, configure_posting_settings
from posting_manager import PostingManager
from repost_from_pinterest_bot.scheduler import run_scheduler_loop


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=config.bot_token.get_secret_value())

    posting_manager = PostingManager(bot, config.bot_settings_file, config.images_root_dir, config.channel_id)

    class AddPostingManagerMiddleware(BaseMiddleware):
        async def __call__(
                self,
                handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
                event: CallbackQuery,
                data: Dict[str, Any]
        ) -> Any:
            data["posting_manager"] = posting_manager
            return await handler(event, data)

    dp.message.middleware(AddPostingManagerMiddleware())
    dp.include_router(start.router)
    dp.include_router(configure_posting_settings.router)

    asyncio.create_task(run_scheduler_loop())
    await asyncio.gather(posting_manager.start(), dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()))


if __name__ == '__main__':
    asyncio.run(main())
