import asyncio
import logging
from typing import Callable, Dict, Any, Awaitable

import aioschedule as schedule
from aiogram import BaseMiddleware
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery

from telegram_logger import TelegramLoggerHandler
from config_reader import config
from handlers import start, configure_posting_settings
from posting_manager import PostingManager
from scheduler import run_scheduler_loop


async def main():
    logger = logging.getLogger('RepostFromPinterestBot')
    logger.setLevel(logging.INFO)
    setup_console_logger(logger)

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=config.bot_token.get_secret_value())

    setup_telegram_logger(bot, dp, logger)

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


def setup_telegram_logger(bot, dp, logger):
    th = TelegramLoggerHandler(bot)
    th_formatter = logging.Formatter('%(levelname)s - %(message)s')
    th.setFormatter(th_formatter)
    logger.addHandler(th)
    schedule.every().second.do(th.send_to_user)

    class AddTelegramLoggerHandlerMiddleware(BaseMiddleware):
        async def __call__(
                self,
                handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
                event: CallbackQuery,
                data: Dict[str, Any]
        ) -> Any:
            data["telegram_logger_handler"] = th
            return await handler(event, data)

    dp.message.middleware(AddTelegramLoggerHandlerMiddleware())


def setup_console_logger(logger):
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)


if __name__ == '__main__':
    asyncio.run(main())
