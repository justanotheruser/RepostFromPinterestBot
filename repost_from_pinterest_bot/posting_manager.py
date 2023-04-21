import logging
from typing import Optional
from aiogram import Bot
import aioschedule as schedule

from bot_settings import BotSettings, load_settings, save_settings
from image_downloader import ImageDownloader
from upload import upload_images_from_dir

logger = logging.getLogger('RepostFromPinterestBot')


class PostingManager:
    CHECK_FOR_DOWNLOADED_IMAGES_EVERY_X_MINUTES = 1

    def __init__(self, bot: Bot, settings_file: str, images_root_dir: str, channel_id: str):
        self.bot = bot
        self.settings_file = settings_file
        self.images_root_dir = images_root_dir
        self.channel_id = channel_id
        self.settings: Optional[BotSettings] = None
        self.uploaded_images = []
        self.image_downloader = None
        self.start_posting_job = None
        self.posting_job = None

    async def start(self):
        #self.settings = load_settings(self.settings_file)
        #if self.settings:
        #    await self._on_settings_changed()
        pass

    async def change_settings(self, settings: BotSettings):
        self.settings = settings
        save_settings(self.settings_file, self.settings)
        await self._on_settings_changed()

    async def _on_settings_changed(self):
        if self.image_downloader is None:
            self.image_downloader = ImageDownloader(self.images_root_dir)
        await self.image_downloader.change_settings(self.settings.pinterest)
        if self.start_posting_job:
            schedule.cancel_job(self.start_posting_job)
        if self.posting_job:
            schedule.cancel_job(self.posting_job)
        self.start_posting_job = schedule.every(
            self.CHECK_FOR_DOWNLOADED_IMAGES_EVERY_X_MINUTES).minutes.do(self.start_posting)

    async def start_posting(self):
        if not self.image_downloader.has_finished():
            logger.warning("Attempt to post images failed because they're not fully downloaded yet")
            return
        schedule.cancel_job(self.start_posting_job)
        if not self.uploaded_images:
            self.uploaded_images = upload_images_from_dir(self.image_downloader.get_current_images_dir())
        self.uploaded_images_gen = self.make_uploaded_images_gen()
        self.posting_job = schedule.every(self.settings.posting.frequency_hours).seconds.do(self.post)

    async def post(self):
        try:
            await self.bot.send_photo(self.channel_id, next(self.uploaded_images_gen))
        except StopIteration:
            logger.info("Finished posing")
            schedule.cancel_job(self.posting_job)

    def make_uploaded_images_gen(self):
        for uploaded_image in self.uploaded_images:
            logger.info(uploaded_image)
            yield uploaded_image
