from django.core.management.base import BaseCommand, CommandError

from main.APIManager import APIManager


class Command(BaseCommand):
    help = 'Cache data from data.gov.sg to database'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--full',
            action='store_true',
            help='Do a full cache for every entry',
        )

    def handle(self, *args, **options):
        api = APIManager()
        # if options['full']:
        #     api.load_data()
        #     api.import_to_database(print_output=True)
        # else:
        #     api.load_data(order="desc")
        #     api.import_to_database(update=True, print_output=True)
