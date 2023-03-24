from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class selenium_entity():

    def __init__(self, **kwargs):

        self.url = kwargs.get('url', '')
        # self.headless = kwargs.get('headless')
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('detach', True)  #不自动关闭浏览器
        self.options.add_argument('--incognito')
        self.options.add_argument("--disable-extensions")
        self.options.add_experimental_option("excludeSwitches", ['enable-automation']);
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')

        self.browser = webdriver.Chrome(options=self.options)

    def browser_run(self, **kwargs):

        if kwargs:
            self.browser.get(kwargs.get('url', ''))
        else:
            self.browser.get(self.url)

    def browser_close(self):

        self.browser.quit()
