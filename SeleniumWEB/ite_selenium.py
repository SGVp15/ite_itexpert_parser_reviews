import asyncio
import functools
from selenium import webdriver
from selenium.common import (NoSuchElementException, ElementClickInterceptedException,
                             StaleElementReferenceException, ElementNotInteractableException,
                             TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from SeleniumWEB.config import LOGIN_MOODLE, PASSWORD_MOODLE
from Utils.chromedriver_autoupdate import ChromedriverAutoupdate


class IteSelenium:
    def __init__(self, base_url=''):
        self.base_url = base_url
        ChromedriverAutoupdate(operatingSystem="win").check()

        options = webdriver.ChromeOptions()
        # Чтобы запускался в свернутом виде, как вы просили ранее:
        options.add_argument("--headless")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--disable-notifications")

        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.base_url)
        self.web_error = (NoSuchElementException, ElementClickInterceptedException,
                          StaleElementReferenceException, ElementNotInteractableException)

    # Вспомогательный метод для запуска синхронных методов Selenium в потоке
    async def _run_async(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        # Используем partial для передачи аргументов в функцию
        p_func = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, p_func)

    async def find_element(self, by, value, timeout=10):
        # Обертка над WebDriverWait
        def _wait():
            wait = WebDriverWait(self.driver, timeout)
            try:
                return wait.until(EC.presence_of_element_located((by, value)))
            except TimeoutException:
                return None

        return await self._run_async(_wait)

    async def authorization(self):
        # Переход на страницу логина
        await self._run_async(self.driver.get, f'{self.base_url}/cabinet/main.php')

        for i in range(2):
            try:
                # Ищем элементы асинхронно
                input_login = await self.find_element(By.Name, value='USER_LOGIN')
                input_password = await self.find_element(By.Name, value='USER_PASSWORD')
                button_enter = await self.find_element(By.Class, value='btn--md btn--mark')

                if input_password and input_login and button_enter:
                    # Выполняем действия в потоке
                    def _fill_form():
                        input_login.clear()
                        input_login.send_keys(LOGIN_MOODLE)
                        input_password.clear()
                        input_password.send_keys(PASSWORD_MOODLE)
                        button_enter.click()

                    await self._run_async(_fill_form)

                await asyncio.sleep(0.2)  # Асинхронная пауза
                break
            except self.web_error:
                if i == 1: raise  # Если на второй попытке ошибка — пробрасываем выше
                await asyncio.sleep(0.5)

    async def get_page_source(self):
        """Метод для безопасного получения исходного кода страницы"""
        return await self._run_async(lambda: self.driver.page_source)

    async def navigate_to(self, url):
        """Метод для перехода по ссылке"""
        await self._run_async(self.driver.get, url)

    async def quit(self):
        """Закрытие браузера"""
        await self._run_async(self.driver.quit)


def xpath_get_button_parrent(class_name: str) -> str:
    return f'//button[.//span[@class="{class_name}"]]'