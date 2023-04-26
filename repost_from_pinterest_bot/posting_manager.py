import logging
from typing import Optional

import aioschedule as schedule
from aiogram import Bot

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
        self.image_downloader: Optional[ImageDownloader] = None
        self.start_posting_job = None
        self.posting_job = None

    async def start(self):
        self.settings = load_settings(self.settings_file)
        if self.settings:
            await self._on_settings_changed()

    async def change_settings(self, settings: Optional[BotSettings]):
        """Change settings for posting. Use settings=None to stop posting."""
        logger.info(f"Настройки изменены на {settings}")
        self.settings = settings
        save_settings(self.settings_file, self.settings)
        await self._on_settings_changed()

    async def _on_settings_changed(self):
        if self.start_posting_job:
            schedule.cancel_job(self.start_posting_job)
        if self.posting_job:
            schedule.cancel_job(self.posting_job)
        if self.uploaded_images:
            self.uploaded_images = None
        if not self.settings:
            if self.image_downloader:
                self.image_downloader.stop_downloading()
            return
        self.start_posting_job = schedule.every(
            self.CHECK_FOR_DOWNLOADED_IMAGES_EVERY_X_MINUTES).minutes.do(self.start_posting)
        logger.info(
            f"Проверяем, что картинки скачались, раз в {self.CHECK_FOR_DOWNLOADED_IMAGES_EVERY_X_MINUTES} минут")
        if self.image_downloader is None:
            self.image_downloader = ImageDownloader(self.images_root_dir)
        await self.image_downloader.change_settings(self.settings.pinterest)

    async def start_posting(self):
        if not self.image_downloader.has_finished():
            logger.warning("Попробовали запостить, но картинки ещё не скачались")
            return
        schedule.cancel_job(self.start_posting_job)
        if not self.uploaded_images:
            self.uploaded_images = upload_images_from_dir(self.image_downloader.get_current_images_dir())
        self.uploaded_images_gen = self.make_uploaded_images_gen()
        await self.post()
        self.posting_job = schedule.every(self.settings.posting.frequency_hours).hours.do(self.post)
        logger.info(f"Запланировали отправку картинок каждые {self.settings.posting.frequency_hours} часов")

    async def post(self):
        try:
            await self.bot.send_photo(self.channel_id, next(self.uploaded_images_gen))
            logger.info(f"Отправили картинку")
        except StopIteration:
            logger.info("Картинки закончились")
            schedule.cancel_job(self.posting_job)

    def make_uploaded_images_gen(self):
        for uploaded_image in self.uploaded_images:
            yield uploaded_image

    def human_readable_settings(self) -> str:
        if not self.settings:
            return 'Сейчас бот не настроен'
        return f'Собираем изображения с Pinterest по ключам {self.settings.pinterest.queries} по ' \
               f'{self.settings.pinterest.number_of_images} штук и отправляем раз в ' \
               f'{self.settings.posting.frequency_hours} час(а/ов) в канал {self.channel_id}'
