from django.core.management.base import BaseCommand, CommandError

from main.APIManager import APIManager
from main.utils.PricePredictionModel import PricePredictionModel


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
        print("Init ppm...")
        ppm = PricePredictionModel()
        inputs = [[100, 3, 3, '80 Years']]  # Area, flat_id_type, level_type_id, lease
        print(ppm.prediction_for_user_input(inputs))
