import logging

from aiogram import Bot

from bot_settings import BotSettings, load_settings, save_settings
from image_downloader import ImageDownloader
from scheduler import JobScheduler
from upload import upload_images_from_dir


class PostingManager:
    def __init__(self, bot: Bot, settings_file: str, images_root_dir: str, channel_id: str):
        self.bot = bot
        self.settings_file = settings_file
        self.images_root_dir = images_root_dir
        self.channel_id = channel_id
        self.scheduler = JobScheduler()
        self.uploaded_images = []
        self.image_downloader = None

    async def start(self):
        settings = load_settings(self.settings_file)
        if settings:
            self.image_downloader = ImageDownloader(settings.pinterest, self.images_root_dir)
            await self.image_downloader.download()
            self.scheduler.reschedule(settings.posting.frequency_hours, self.post_images)
        else:
            logging.error('Failed to load settings')
            # TODO: send email

    async def change_settings(self, settings: BotSettings):
        if self.image_downloader is None:
            self.image_downloader = ImageDownloader(settings.pinterest, self.images_root_dir)
        await self.image_downloader.change_settings(settings.pinterest)
        save_settings(self.settings_file, settings)
        self.scheduler.reschedule(settings.posting.frequency_hours, self.post_images)

    async def post_images(self):
        if not self.image_downloader.has_finished():
            logging.warning("Attempt to post images failed because they're not fully downloaded yet")
            return
        if not self.uploaded_images:
            self.uploaded_images = upload_images_from_dir(self.image_downloader.get_current_images_dir())
        for uploaded_image in self.uploaded_images:
            await self.bot.send_photo(self.channel_id, uploaded_image)
