from save_images import save_pin
from utils import setup_logger, create_firefox_driver

if __name__ == '__main__':
    setup_logger()
    driver = create_firefox_driver()
    try:
        save_pin(driver, 'testing_imgs', 'https://ru.pinterest.com/pin/690317449150425738/')
    finally:
        driver.close()
        driver.quit()
