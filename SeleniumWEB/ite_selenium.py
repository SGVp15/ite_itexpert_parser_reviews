import time

from selenium import webdriver
from selenium.common import (NoSuchElementException, ElementClickInterceptedException,
                             StaleElementReferenceException, ElementNotInteractableException,
                             TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from SeleniumWEB.config import LOGIN_ITE as LOGIN, PASSWORD_ITE as PASSWORD, ITEXPERT_URL
from Utils.chromedriver_autoupdate import ChromedriverAutoupdate


class IteSelenium:
    def __init__(self, base_url=''):
        self.base_url = base_url
        if not self.base_url:
            self.base_url = ITEXPERT_URL
        ChromedriverAutoupdate(operatingSystem="win").check()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--disable-notifications")

        self.driver = webdriver.Chrome(options=options)
        self.web_error = (NoSuchElementException, ElementClickInterceptedException,
                          StaleElementReferenceException, ElementNotInteractableException)

    def find_element(self, by, value, timeout=10):
        def _wait():
            wait = WebDriverWait(self.driver, timeout)
            try:
                return wait.until(EC.presence_of_element_located((by, value)))
            except TimeoutException:
                return None

        return _wait()

    def authorization(self):
        self.driver.get(f'{self.base_url}/cabinet/main.php')

        time.sleep(1)
        for i in range(2):
            try:
                input_login = self.find_element(By.NAME, value='USER_LOGIN')
                input_password = self.find_element(By.NAME, value='USER_PASSWORD')
                button_enter = self.find_element(By.CSS_SELECTOR, "input.btn--md.btn--mark")

                if input_password and input_login and button_enter:
                    def _fill_form():
                        input_login.clear()
                        input_login.send_keys(LOGIN)
                        input_password.clear()
                        input_password.send_keys(PASSWORD)
                        button_enter.click()

                    _fill_form()

                time.sleep(2)
                break
            except self.web_error:
                if i == 1: raise
                time.sleep(0.5)

    def get_page_source(self):
        self.driver.get(f'{self.base_url}/cabinet/adminka.php')
        return self.driver.page_source

    def quit(self):
        self.driver.quit()
