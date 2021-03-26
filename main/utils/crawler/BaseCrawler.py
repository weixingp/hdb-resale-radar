import os

from main.models import NewsArticle
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options


class BaseCrawler:
    articles = []
    source = "Undefined"
    browser = None
    search_url = None

    def __init__(self):
        options = Options()
        browser_path = os.getenv("BROWSER_PATH")
        options.headless = True
        self.browser = webdriver.Chrome(options=options, executable_path=browser_path)
        self.browser.set_page_load_timeout(60)

    def get_articles(self, n):
        """
        This function should be implemented in a way to save a list of dictionaries into self.articles
        Each dictionary must contain url, title, summary and image_url
        """
        raise Exception("get_article_content fn not implemented.")

    def save_to_db(self):
        if not self.articles:
            raise ValueError("Articles not loaded yet.")

        for article in self.articles:
            try:
                crawled = NewsArticle.objects.filter(
                    url=article['url']
                )

                if not crawled:
                    NewsArticle.objects.create(
                        url=article['url'],
                        title=article['title'],
                        summary=article['summary'],
                        img_url=article['img_url'],
                        source=self.source,
                    )
            except KeyError:
                # Log
                print("Article does not contain required items.")
                continue
