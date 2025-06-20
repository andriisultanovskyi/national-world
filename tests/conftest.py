import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import shutil
import logging
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException


# Logging settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    # options.add_argument("--headless=new")
    # options.add_argument("--headless=old")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # driver = webdriver.Chrome(options=options)
    return driver



@pytest.fixture
def close_cookie_popup(driver):
    driver.implicitly_wait(10)
    iframe = driver.find_element(By.ID, "sp_message_iframe_1323424")
    driver.switch_to.frame(iframe)
    button = driver.find_element(By.XPATH, ".//button[contains(text(), 'Accept')]")
    button.click()
    driver.switch_to.default_content()


@pytest.fixture()
def driver():
    driver = create_driver()
    driver.get('https://www.nationalworld.com/')

    try:
        # Waiting for popup to appear
        WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        print("Popup found, try to close...")
        alert = driver.switch_to.alert
        alert.accept()
        # Waiting for "Accept" button will be clickable
        # accept_button = WebDriverWait(driver, timeout).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, "accept-all"))
        # )
        # accept_button.click()
        print("Popup closed.")
    except TimeoutException:
        print("Popup did not appear - continue the test")

    driver.maximize_window()
    time.sleep(10)
    yield driver
    time.sleep(1)
    try:
        driver.quit()
    except Exception as e:
        logger.warning(f"[!] Exception during driver.quit(): {e}")


@pytest.fixture()
def switch_to_new_window_home(driver):
    """Waits for a new window to open and switches to it"""
    def _switch():
        WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
        windows = driver.window_handles
        print(f"Open windows: {windows}")
        if len(windows) > 1:
            driver.switch_to.window(windows[1])
        else:
            pytest.fail("New window did not open")
    return _switch


# Test fall hook
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Automatic screenshot when test fails.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:

        driver = None
        for fixture_name, fixture_value in item.funcargs.items():
            if hasattr(fixture_value, "save_screenshot"):
                driver = fixture_value
                break

        if driver:
            if not os.path.exists("../screenshots"):
                os.makedirs("../screenshots")

            screenshot_path = os.path.join("../screenshots", f"{item.name}.png")
            driver.save_screenshot(screenshot_path)
            logger.info(f"[!] Screenshot saved: {screenshot_path}")
        else:
            logger.warning("[!] Screenshot NOT saved: Driver not found in fixtures.")



