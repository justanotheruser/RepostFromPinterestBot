import fnmatch
import logging
import os

from aiogram.types import FSInputFile

logger = logging.getLogger('RepostFromPinterestBot')


def upload_images_from_dir(images_dir):
    logger.info(f'Загружаем картинки из {images_dir} на сервер Телеграма')
    uploaded_images = []
    for root, dirs, files in os.walk(os.path.expanduser(images_dir)):
        for extension in ('*.jpg', '*.png'):
            for filename in fnmatch.filter(files, extension):
                filepath = os.path.join(root, filename)
                if os.path.isfile(filepath):
                    logger.info(f'Загружаем {filepath}')
                    uploaded_images.append(FSInputFile(filepath))
    return uploaded_images
