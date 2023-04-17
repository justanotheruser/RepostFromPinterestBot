import contextlib
import logging
import sys
import os

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def create_firefox_driver(headless=True):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument('-headless')
    driver = webdriver.Firefox(options=options, service_log_path=os.devnull)
    logging.info('Firefox driver created')
    return driver


@contextlib.contextmanager
def second_tab(driver, url):
    original_window_handle = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get(url)
    logging.info(f'Opened {driver.current_url} in another tab')
    yield
    driver.close()
    driver.switch_to.window(original_window_handle)
    WebDriverWait(driver, 1).until(EC.number_of_windows_to_be(1))


def setup_logger(loglevel=logging.INFO, filename: str = None):
    if filename:
        handler = logging.FileHandler(filename, mode='a', encoding='utf-8')
    else:
        handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(loglevel)
    handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    logger.addHandler(handler)
