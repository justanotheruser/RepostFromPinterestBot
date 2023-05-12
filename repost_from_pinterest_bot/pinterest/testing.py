import logging
import os
import threading
import sys

from save_images import save_pin, save_images
from utils import create_firefox_driver


def make_dirs():
    dir_path = os.path.dirname(__file__)
    testing_images_dir = os.path.join(dir_path, 'testing_imgs')
    os.makedirs(testing_images_dir, exist_ok=True)
    failed_pages_dir = os.path.join(dir_path, 'failed_pages')
    os.makedirs(failed_pages_dir, exist_ok=True)
    return testing_images_dir, failed_pages_dir


def test_save_pin():
    driver = create_firefox_driver()
    testing_images_dir, failed_pages_dir = make_dirs()
    try:
        save_pin(driver, testing_images_dir, 'https://ru.pinterest.com/pin/690317449150425738/', failed_pages_dir)
    finally:
        driver.close()
        driver.quit()


def test_save_images():
    testing_images_dir, failed_pages_dir = make_dirs()
    stop_downloading_event_stub = threading.Event()
    save_images('новинки маникюр', max_images=80, output_dir=testing_images_dir, failed_pages_dir=failed_pages_dir,
                stop_downloading=stop_downloading_event_stub, headless=True)


def test_same_image_in_different_search_requests():
    testing_images_dir, failed_pages_dir = make_dirs()
    stop_downloading_event_stub = threading.Event()
    save_images('мемы', max_images=1, output_dir=testing_images_dir, failed_pages_dir=failed_pages_dir,
                stop_downloading=stop_downloading_event_stub, headless=True)
    save_images('смешные мемы', max_images=4, output_dir=testing_images_dir, failed_pages_dir=failed_pages_dir,
                stop_downloading=stop_downloading_event_stub, headless=True)


def test_get_pin_id():
    driver = create_firefox_driver()
    testing_images_dir, failed_pages_dir = make_dirs()
    try:
        save_pin(driver, testing_images_dir, 'https://ru.pinterest.com/pin/1023161609073882968/?mt=login',
                 failed_pages_dir)
    finally:
        driver.close()
        driver.quit()


def setup_logger(loglevel=logging.INFO):
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(loglevel)
    handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    logger.addHandler(handler)


if __name__ == '__main__':
    setup_logger()
    test_same_image_in_different_search_requests()
