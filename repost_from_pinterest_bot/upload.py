import fnmatch
import logging
import os

from aiogram.types import FSInputFile


def upload_images_from_dir(images_dir):
    logging.info(f'Uploading images from {images_dir}')
    uploaded_images = []
    for root, dirs, files in os.walk(images_dir):
        for extension in ('*.jpg', '*.png'):
            for filename in fnmatch.filter(files, extension):
                filepath = os.path.join(root, filename)
                if os.path.isfile(filepath):
                    logging.info(f'Uploading {filepath}')
                    uploaded_images.append(FSInputFile(filepath))
    return uploaded_images
