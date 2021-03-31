import os

from main.models import NewsArticle
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options

from main.utils.crawler.BaseCrawler import BaseCrawler


class BrowserCrawler(BaseCrawler):
    __browser = None

    def __init__(self):
        options = Options()
        browser_path = os.getenv("BROWSER_PATH")
        options.headless = True
        self.__browser = webdriver.Chrome(options=options, executable_path=browser_path)
        self.__browser.set_page_load_timeout(60)
