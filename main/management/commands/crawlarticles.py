from django.core.management.base import BaseCommand, CommandError

from main.utils.crawler.MotherShip import MotherShipCrawler
from main.utils.crawler.StraitsTimes_express import StraitsTimesCrawler


class Command(BaseCommand):
    help = 'Crawl news articles related to HDB resale.'

    def handle(self, *args, **options):
        crawlers = [
            StraitsTimesCrawler(),
            MotherShipCrawler(),
        ]

        for crawler in crawlers:
            print(f"Starting {crawler.source} crawler...")
            try:
                crawler.get_articles(n=10)
                crawler.save_to_db()
            except Exception as ex:
                print("Some errors have occurred: " + repr(ex))
            print(f"Finished crawling {crawler.source}")

