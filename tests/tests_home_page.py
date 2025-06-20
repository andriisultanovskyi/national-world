import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time



# def test_close_popup(driver):
#     driver.implicitly_wait(10)
#     iframe = driver.find_element(By.ID, "sp_message_iframe_1323424")
#     driver.switch_to.frame(iframe)
#     button = driver.find_element(By.XPATH, ".//button[contains(text(), 'Accept')]")
#     button.click()
#     driver.switch_to.default_content()




# The test checks the click of the "Test" button on the header and goes to the 'Test for Students' page
def test_click_button_news(driver, close_cookie_popup):
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "News"))
    )
    element.click()
    WebDriverWait(driver, 10).until(EC.url_contains("news"))
    assert "https://www.nationalworld.com/news" in driver.current_url





