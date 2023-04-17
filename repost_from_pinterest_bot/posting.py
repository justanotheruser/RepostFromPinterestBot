import asyncio
import logging
from typing import Optional

import aioschedule as schedule
from aiogram import Bot

from repost_from_pinterest_bot.upload import upload_images_from_dir


async def run_scheduler_loop():
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


class PostingScheduler:
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.channel_id: Optional[str] = None
        self.job: Optional[schedule.Job] = None
        self.current_images_dir: Optional[str] = None
        self.uploaded_images = []

    def configure(self, bot: Bot, channel_id: str):
        self.bot = bot
        self.channel_id = channel_id

    async def post_images(self):
        if not self.uploaded_images:
            self.uploaded_images = upload_images_from_dir(self.current_images_dir)
        for uploaded_image in self.uploaded_images:
            await self.bot.send_photo(self.channel_id, uploaded_image)

    def reschedule(self, hours: int):
        if hours > 0:
            if self.job:
                schedule.cancel_job(self.job)
            logging.info(f'Scheduled posting every {hours} hour(s)')
            # TODO: seconds->hours
            self.job = schedule.every(hours).seconds.do(self.post_images)


scheduler = PostingScheduler()
