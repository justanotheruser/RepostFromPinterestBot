import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot_settings import load_settings
from config_reader import config
from handlers import start, configure_posting_settings
from repost_from_pinterest_bot.posting import run_scheduler_loop, scheduler


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot_settings = load_settings(config.bot_settings_file)
    if not bot_settings:
        logging.critical('Failed to load settings')
        # TODO: send email
        return

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=config.bot_token.get_secret_value())

    asyncio.create_task(run_scheduler_loop())
    scheduler.configure(bot, config.channel_id)
    scheduler.reschedule(bot_settings.posting.frequency_hours)

    dp.include_router(start.router)
    dp.include_router(configure_posting_settings.router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
