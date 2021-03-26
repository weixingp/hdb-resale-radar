from itertools import chain

import requests
from bs4 import BeautifulSoup

from selenium.common.exceptions import NoSuchElementException
import time

from main.utils.crawler.BaseCrawler import BaseCrawler
from datetime import datetime


class MotherShipCrawler(BaseCrawler):
    search_url = "https://mothership.sg/search/?s=resale+flat"
    source = "MotherShip"

    def get_articles(self, n):
        browser = self.browser
        browser.get(self.search_url)
        page_number = 1
        urls = []

        # code to press the button load more results for mothership
        while True:
            # try block helps to click the load more results, page number is set to prevent errors where load more results keeps going
            try:
                button = browser.find_element_by_css_selector("#load-more")
                button.click()
                time.sleep(2)
                page_number += 1
                if page_number == 9:
                    break

            # error checking so that no error occurs
            except NoSuchElementException:
                break

        # code to print out the urls after loading more results
        css_counter = 1
        while True:
            try:
                css = "#search-results > div:nth-child(" + str(
                    css_counter) + ") > div.ind-article > div > div.header > h1 > a"
                css_counter += 1
                links = browser.find_element_by_css_selector(css)
                urls.append(links.get_attribute('href'))

            # error checking to prevent selenium error
            except NoSuchElementException:
                break

        browser.close()

        j = 0
        hdb_flat_crawled = []
        for i in urls:
            if j > n - 1:
                break

            URL = urls[j]
            page = requests.get(URL)
            soup = BeautifulSoup(page.text, 'html.parser')

            image = None
            title = None

            for item2 in soup.find_all('figure', class_='featured-image'):
                image = item2.img['src']

            empty_list = []

            for item2 in soup.find_all('title'):
                title = item2.string

            for item2 in soup.find_all('p'):
                if item2.string is not None:
                    if len(item2.string) > 100:
                        y = item2.string.split()[:]
                        empty_list.append(y)

            final = list(chain.from_iterable(empty_list))
            final = (final[:100])
            summary = ' '.join(final)

            # Post-processing
            title = str(title.string)
            title = title.split(" - Mothership.SG")[0]

            articleDate = None
            try:
                for item2 in soup.find('span', class_='publish-date'):
                    if item2 == '\n':
                        continue

                    articleDateStr = str(item2.string)
                    articleDateStrWON = articleDateStr.strip()
                    articleDateStrWO = articleDateStrWON.replace(',', '')

                    if articleDateStrWO == 'None' or '\n' in articleDateStrWO:
                        continue
                    else:
                        articleDate = datetime.strptime(articleDateStrWO, '%B %d %Y %I:%M %p')
            except Exception:
                pass

            hdb_flat_dictionary = {
                "img_url": image,
                "title": title,
                "summary": summary,
                "url": URL,
                "article_date": articleDate
            }

            hdb_flat_crawled.append(hdb_flat_dictionary)
            j += 1

        self.articles = hdb_flat_crawled
