import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from pages.homepage import HomePage




# The test checks the click of the "Test" button on the header and goes to the 'Test for Students' page
def test_click_button_news(driver, close_cookie_popup):
    homepage = HomePage(driver)
    homepage.open()
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "News"))
    )
    element.click()
    WebDriverWait(driver, 10).until(EC.url_contains("news"))
    assert "https://www.nationalworld.com/news" in driver.current_url





