import contextlib
import logging
import os
import time
import uuid

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger('RepostFromPinterestBot.Pinterest')


def create_firefox_driver(headless=True):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument('-headless')
    driver = webdriver.Firefox(options=options, service_log_path=os.devnull)
    logger.info('Firefox driver created')
    return driver


@contextlib.contextmanager
def second_tab(driver: WebDriver, url, failed_pages_dir: str):
    original_window_handle = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get(url)
    logger.info(f'Opened {driver.current_url}')
    try:
        yield
    except Exception as e:
        logger.error(e)
        os.makedirs(failed_pages_dir, exist_ok=True)
        page_file = os.path.join(failed_pages_dir, f'{uuid.uuid4()}.html')
        with open(page_file, mode='w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f'Сохранили проблемную страницу как {page_file}')
    finally:
        driver.close()
        driver.switch_to.window(original_window_handle)
        WebDriverWait(driver, 1).until(EC.number_of_windows_to_be(1))


def wait_until_completion(driver, retries=20) -> None:
    """waits until the page have completed loading"""
    try:
        state = ""
        attempt = 0
        while state != "complete" or attempt < retries:
            time.sleep(0.5)
            state = driver.execute_script("return document.readyState")
            attempt += 1
    except Exception as ex:
        logger.exception('Error at wait_until_completion: {}'.format(ex))
