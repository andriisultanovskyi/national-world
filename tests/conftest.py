import pytest
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException


# Logging settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_driver():
    options = Options()
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    # options.add_argument("--headless=new")
    # options.add_argument("--headless=old")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


@pytest.fixture
def close_cookie_popup(driver):
    wait = WebDriverWait(driver, 10)
    try:
        iframe = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//iframe[contains(@id, 'sp_message_iframe')]")
        ))
        driver.switch_to.frame(iframe)
        button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, ".//button[contains(text(), 'Accept')]")
        ))
        button.click()
        driver.switch_to.default_content()
    except TimeoutException:
        print("Cookie popup iframe or button not found — continuing test.")
        driver.switch_to.default_content()
    except NoSuchElementException:
        print("Cookie popup button not found after switching to iframe — continuing test.")
        driver.switch_to.default_content()


@pytest.fixture()
def driver():
    driver = create_driver()
    # driver.get('https://www.nationalworld.com/')
    driver.maximize_window()
    yield driver
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



