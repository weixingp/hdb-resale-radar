from django.core.management.base import BaseCommand, CommandError

from main.utils.crawler.MotherShip import MotherShipBaseCrawler
from main.utils.crawler.StraitsTimes import StraitsTimesBaseCrawler


class Command(BaseCommand):
    help = 'Crawl news articles related to HDB resale.'

    def handle(self, *args, **options):
        crawlers = [
            StraitsTimesBaseCrawler(),
            MotherShipBaseCrawler(),
        ]

        for crawler in crawlers:
            print(f"Starting {crawler.source} crawler...")
            crawler.get_articles(n=10)
            crawler.save_to_db()
            print(f"Finished crawling {crawler.source}")

