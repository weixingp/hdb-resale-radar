from selenium.common.exceptions import NoSuchElementException

from main.utils.crawler.CrawlerInterface import CrawlerInterface


class StraitsTimesCrawler(CrawlerInterface):
    source = "Straits Times"
    search_url = "https://www.straitstimes.com/search?searchkey=resale%20flats"

    def get_articles(self, n):
        browser = self.browser
        browser.get(self.search_url)
        url_list = []

        # code to print out the urls after loading more results
        css_counter = 2
        hdb_flat_crawled = []

        # pulling all the urls first using this code
        while True:
            running_counter = 0
            try:
                css = "#resultdata > div:nth-child(" + str(css_counter) + ") > a"
                css_counter += 1
                links = browser.find_element_by_css_selector(css)
                url_list.append(links.get_attribute('href'))
            except NoSuchElementException:
                break

        counter = 1
        for x in url_list:
            if counter > n:
                break
            urls = x
            browser.get(urls)
            try:
                # to produce image for each url
                img = browser.find_element_by_css_selector(
                    "#block-system-main > div > div > div > div.media-group.fadecount0 > div > div > figure > picture > img")
                img_url = img.get_attribute("src")

                # to produce title for each url
                title = browser.find_element_by_css_selector("#block-system-main > div > div > div > header > h1")

                # to produce summary for each url
                summary = browser.find_element_by_css_selector(
                    '#block-system-main > div > div > div > div.group-ob-readmore > div.field-name-body-linked.field.field-name-body.field-type-text-with-summary.field-label-hidden > div.field-items > div > p:nth-child(1)')

                hdb_flat_dictionary = {
                    "img_url": img_url,
                    "title": title.text,
                    "summary": summary.text,
                    "url": x
                }

                hdb_flat_crawled.append(hdb_flat_dictionary)

            except Exception:
                continue

            counter += 1

        browser.close()
        self.articles = hdb_flat_crawled
