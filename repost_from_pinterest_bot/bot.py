import asyncio
import logging
import os

import aioschedule as schedule
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from handlers import start, configure_posting_settings
from middlewares.add_posting_manager import AddPostingManagerMiddleware
from middlewares.add_telegram_logger_handler import AddTelegramLoggerHandlerMiddleware
from middlewares.check_access_rights import CheckAccessRightsMiddleware
from posting_manager import PostingManager
from scheduler import run_scheduler_loop
from telegram_logger import TelegramLoggerHandler


async def main():
    logger = logging.getLogger('RepostFromPinterestBot')
    logger.setLevel(logging.INFO)
    setup_console_logger(logger)
    setup_file_logger(logger)
    logger.info(f'Запускаемся с конфигом {config}')

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=config.bot_token.get_secret_value())

    setup_telegram_logger(bot, dp, logger)

    posting_manager = PostingManager(bot, config.bot_settings_file, config.images_root_dir, config.failed_pages_dir,
                                     config.channel_id)

    dp.update.outer_middleware(CheckAccessRightsMiddleware([config.bot_admin_user_id]))
    dp.message.middleware(AddPostingManagerMiddleware(posting_manager))
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
    dp.message.middleware(AddTelegramLoggerHandlerMiddleware(th))


def setup_console_logger(logger):
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)


def setup_file_logger(logger):
    ch = logging.FileHandler('RepostFromPinterestBot.log', encoding='utf-8')
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)


if __name__ == '__main__':
    os.system("kill -9 $(ps ax | grep firefox | fgrep -v grep | awk '{ print $1 }')")
    asyncio.run(main())
