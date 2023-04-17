import fnmatch
import os

from aiogram.types import FSInputFile


def upload_images_from_dir(images_dir):
    uploaded_images = []
    for root, dirs, files in os.walk(images_dir):
        for extension in ('*.jpg', '*.png'):
            for filename in fnmatch.filter(files, extension):
                filepath = os.path.join(root, filename)
                if os.path.isfile(filepath):
                    uploaded_images.append(FSInputFile(filepath))
    return uploaded_images