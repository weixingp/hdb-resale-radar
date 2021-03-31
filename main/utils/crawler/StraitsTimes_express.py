from datetime import datetime

import requests

from main.utils.crawler.BaseCrawler import BaseCrawler


class StraitsTimesCrawler(BaseCrawler):
    __source = "Straits Times"
    __search_url = "https://api.queryly.com/json.aspx"

    def get_articles(self, n):
        params = {
            "queryly_key": "a7dbcffb18bb41eb",
            "query": "resale flats",
            "endindex": 0,
            "batchsize": n,
            "groupstimezoneoffset": -450,
            "showfaceted": True,
        }

        res = requests.get(url=self.__search_url, params=params)
        if res.status_code != 200:
            raise Exception("HTTP error while getting articles")

        data = res.json()
        articles = data['items']
        for article in articles:
            date = datetime.fromtimestamp(article["pubdateunix"])
            temp = {
                "img_url": article['image'],
                "title": article["title"],
                "summary": article["description"],
                "url": article["link"],
                "article_date": date,
            }
            self.__articles.append(temp)

