import logging
import os
import time
import typing
import uuid
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException

from repost_from_pinterest_bot.pinterest.utils import create_firefox_driver, second_tab, setup_logger

SIGNUP_MODAL_POPUP_XPATH = '//div[@data-test-id="fullPageSignupModal"]'
SIGNUP_MODAL_POPUP_CLOSE_BTN_XPATH = '//div[@data-test-id="full-page-signup-close-button"]/button'
PIN_LINK_XPATH = '//div[@class="gridCentered"]//div[@data-test-id="pin"]//a'
PIN_IMAGE_XPATH = '//div[@id="mweb-unauth-container"]//div[@data-test-id="closeup-body-landscape"]//img'

logger = logging.getLogger('RepostFromPinterestBot.Pinterest')


def get_pinterest_search_url(query: str):
    return f'https://ru.pinterest.com/search/pins/?q={query}&rs=typed'


def close_signup_modal_popup(driver: WebDriver):
    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, SIGNUP_MODAL_POPUP_XPATH)))
    except TimeoutException:
        # No popup
        return
    logger.info('Modal popup about signing up is detected')
    popup = driver.find_element(By.XPATH, SIGNUP_MODAL_POPUP_XPATH)
    close_btn = popup.find_element(By.XPATH, SIGNUP_MODAL_POPUP_CLOSE_BTN_XPATH)
    close_btn.click()
    logger.info('Model popup about signing up is closed')


def save_screenshot(el, output_dir: str, file_path: str):
    file_path = os.path.join(output_dir, file_path)
    with open(file_path, 'wb') as file:
        file.write(el.screenshot_as_png)
    logger.info(f"Сохранили картинку {file_path}")


def save_pin(driver, output_dir: str, pin_link: str):
    with second_tab(driver, pin_link):
        close_signup_modal_popup(driver)

        # Scroll down an up to get rid of 'Show similar' popup at the bottom
        scroll_down(driver)
        time.sleep(0.1)
        scroll_up(driver)

        pin_uuid = str(uuid.uuid4())
        img_el = driver.find_element(By.XPATH, PIN_IMAGE_XPATH)
        save_screenshot(img_el, output_dir, f'{pin_uuid}.png')


def save_from_displayed_search_results(driver: WebDriver, already_saved: typing.Set[str], max_images: int,
                                       output_dir: str) -> typing.Set[str]:
    """
    :param driver: Selenium WebDriver instance
    :param already_saved: Links to already saved pins
    :param max_images: Save at most this many
    :param output_dir: Path to folder where images will be saved (should exist)
    :return: set of links to saved pins
    """
    saved_pins = set()
    pin_link_els = driver.find_elements(By.XPATH, PIN_LINK_XPATH)
    for pin_link_el in pin_link_els:
        if len(saved_pins) >= max_images:
            break
        pin_link = pin_link_el.get_attribute('href')
        if pin_link in already_saved or pin_link in saved_pins:
            continue
        save_pin(driver, output_dir, pin_link)
        saved_pins.add(pin_link)
    return saved_pins


def scroll_down(driver: WebDriver, y_pos=None):
    if not y_pos:
        y_pos = 'document.body.scrollHeight'
    logger.debug(f'Scroll down to {y_pos}')
    driver.execute_script(f"window.scrollTo(0,{y_pos});")


def scroll_up(driver: WebDriver):
    logger.debug('Scroll up')
    driver.execute_script("window.scrollTo(0,0);")


def do_save_images(driver: WebDriver, query: str, max_images: int, output_dir: str):
    """
    :param driver: WebDriver instance
    :param query: Search query
    :param max_images: Save at most this many
    :param output_dir: Path to folder where images will be saved (should exist)
    """
    logger.info(f'save_pinterest_images is called: query={query}, max_images={max_images}, dir_path={output_dir}')
    driver.get(get_pinterest_search_url(query))
    logger.info(f'Открыли {driver.current_url}')
    all_saved_pin_links = set()
    while len(all_saved_pin_links) < max_images:
        saved_pin_links = save_from_displayed_search_results(
            driver, all_saved_pin_links, max_images - len(all_saved_pin_links), output_dir)
        if len(saved_pin_links) == 0:
            if len(all_saved_pin_links) == 0:
                logger.warning("Не нашли ни одной картинки")
            else:
                logger.warning(f'Не нашли новых картинок до того, как набрали {max_images}')
            break
        else:
            logger.info(f'Сохранили {len(saved_pin_links)} картинок')
        all_saved_pin_links.update(saved_pin_links)
        scroll_down(driver)
    logger.debug(all_saved_pin_links)


def save_images(query: str, max_images: int, output_dir: str):
    """
    :param query: Search query
    :param max_images: Save at most this many
    :param output_dir: Path to folder where images will be saved (should exist)
    """
    browser = create_firefox_driver(headless=True)
    try:
        browser.set_window_size(1350, 3000)
        do_save_images(browser, query=query, max_images=max_images, output_dir=output_dir)
    except Exception as e:
        logger.critical(e)
    browser.close()
    browser.quit()
    logger.info('Закрыли браузер')


if __name__ == '__main__':
    setup_logger()
    firefox = create_firefox_driver(headless=True)
    output_dir_name = datetime.today().strftime('%d.%m.%Y')
    output_dir_name = os.path.join('temp', output_dir_name)
    try:
        firefox.set_window_size(1350, 3000)
        do_save_images(firefox, query='мемы', max_images=5, output_dir=output_dir_name)
    except Exception as e:
        logging.critical(e)
    firefox.close()
    firefox.quit()
    logging.info('Browser quit')