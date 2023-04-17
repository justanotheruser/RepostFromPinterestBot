import asyncio
import logging
import typing

import aioschedule as schedule
from aiogram import Bot


async def run_scheduler_loop():
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


class PostingScheduler:
    def __init__(self):
        self.bot: typing.Optional[Bot] = None
        self.channel_id: typing.Optional[str] = None
        self.job: typing.Optional[schedule.Job] = None

    def configure(self, bot: Bot, channel_id: str):
        self.bot = bot
        self.channel_id = channel_id

    async def post_images(self):
        await self.bot.send_message(self.channel_id, 'Hello!')

    def reschedule(self, hours):
        if hours > 0:
            if self.job:
                schedule.cancel_job(self.job)
            logging.info(f'Scheduled posting every {hours} hour(s)')
            # TODO: hours
            self.job = schedule.every(hours).seconds.do(self.post_images)


scheduler = PostingScheduler()
