from main.models import NewsArticle


class BaseCrawler:
    __articles = []
    __source = "Undefined"
    __search_url = None

    def get_articles(self, n):
        """
        This function should be implemented in a way to save a list of dictionaries into self.articles
        Each dictionary must contain url, title, summary and image_url
        """
        raise Exception("get_article_content fn not implemented.")

    def save_to_db(self):
        if not self.__articles:
            raise ValueError("Articles not loaded yet.")

        for article in self.__articles:
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
                        source=self.__source,
                        date=article['article_date']
                    )
            except KeyError:
                # Log
                print("Article does not contain required items.")
                continue
