import asyncio
import logging
import os
import shutil
from datetime import datetime

from bot_settings import BotSettings
from pinterest.save_images import save_images


def create_empty_dir(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        logging.info(f'Deleting existing dir {dir_path}')
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
    logging.info(f'Created dir {dir_path}')


class ImageDownloader:
    def __init__(self, settings: BotSettings.Pinterest, images_root_dir: str):
        self.settings = settings
        self.images_root_dir = images_root_dir
        self.current_images_dir = None

    async def download(self):
        if not self.settings.queries:
            return
        self.current_images_dir = None
        await asyncio.to_thread(self._blocking_download)

    def _blocking_download(self):
        create_empty_dir(self.images_root_dir)
        downloads_dir = os.path.join(self.images_root_dir, datetime.today().strftime('%d.%m.%Y'))
        for query in self.settings.queries:
            save_images(query, self.settings.number_of_images, downloads_dir)
        self.current_images_dir = downloads_dir

    async def change_settings(self, settings: BotSettings.Pinterest):
        if self.settings != settings:
            await self.download()

    def has_finished(self):
        return self.current_images_dir is not None

    def get_current_images_dir(self):
        return self.current_images_dir
