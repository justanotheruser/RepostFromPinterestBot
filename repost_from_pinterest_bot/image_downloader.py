import asyncio
import logging
import os
import shutil
from datetime import datetime
from typing import Optional
import threading
from bot_settings import BotSettings
from pinterest.save_images import save_images

logger = logging.getLogger('RepostFromPinterestBot')


def create_empty_dir(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        logger.info(f'Удаляем папку {dir_path}')
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
    logger.info(f'Создали папку {dir_path}')


class ImageDownloader:
    def __init__(self, images_root_dir: str):
        self.images_root_dir = images_root_dir
        self.current_images_dir = None
        self.settings: Optional[BotSettings.Pinterest] = None
        self.stop_downloading_event = threading.Event()

    async def download(self):
        if not self.settings or not self.settings.queries:
            return
        self.stop_downloading_event.clear()
        self.current_images_dir = None
        await asyncio.to_thread(self._blocking_download)

    def _blocking_download(self):
        downloads_dir = os.path.join(self.images_root_dir, datetime.today().strftime('%d.%m.%Y'))
        create_empty_dir(downloads_dir)
        for query in self.settings.queries:
            save_images(query, self.settings.number_of_images, downloads_dir, self.stop_downloading_event)
        self.current_images_dir = downloads_dir

    async def change_settings(self, settings: BotSettings.Pinterest):
        self.settings = settings
        await self.download()

    def has_finished(self):
        return self.current_images_dir is not None

    def get_current_images_dir(self):
        return self.current_images_dir

    def stop_downloading(self):
        self.stop_downloading_event.set()
