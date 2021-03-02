import re

import requests

from main.models import Town, BlockAddress, FlatType, LevelType
from main.utils.OneMapAPI import OneMapAPI


class APIManager:
    resource_id = '42ff9cfe-abe5-4b54-beda-c88f9bb438ee'  # Resale HDB data
    base_url = "https://data.gov.sg/api/action/datastore_search"  # SG Gov Data API

    def __init__(self):
        self.full_data = []
        if not self.test_connection():
            raise Exception("Unable to initiate APIManager, API Server down.")

    def test_connection(self):
        connection = requests.get(self.base_url, params={"resource_id": self.resource_id})
        if connection.status_code == 200:
            if connection.json()['success']:
                return True
            else:
                return False
        else:
            return False

    def load_data(self):
        full_data = []
        total = requests.get(
            self.base_url,
            params={'resource_id': self.resource_id, 'limit': 1}
        ).json()['result']['total']

        limit = 10000
        offset = 0
        while offset < total:
            payload = {'resource_id': self.resource_id, 'limit': limit, 'offset': offset}
            resp = requests.get(self.base_url, params=payload)
            data = resp.json()
            if data['success']:
                temp_data = data['result']['records']
                full_data += temp_data
                offset += data['result']['limit']
            else:
                raise Exception("Error from api")

        self.full_data = full_data
        return full_data

    def import_to_database(self):
        if not self.full_data:
            return False

        one_map = OneMapAPI()
        level_options = {
            '01 TO 03': 'Very Low',
            '04 TO 06': 'Low',
            '07 TO 09': 'Intermediate',
            '10 TO 12': 'High',
            'others': 'Very High',
            'undefined': 'Undefined'
        }

        for room in self.full_data:
            # Process town data
            town = room['town']
            town_obj, created = Town.objects.get_or_create(
                name=town
            )

            # Process address data
            block = room['block']
            street_name = room['street_name']

            block_obj, created = BlockAddress.objects.get_or_create(
                block=block,
                street_name=street_name,
                town_name_id=town_obj,
            )

            # Coord data is only queried when new block address is created.
            if created:
                coord = one_map.get_coordinates(block + " " + street_name)
                latitude = coord['lat']
                longitude = coord['long']
                block_obj.latitude = latitude
                block_obj.longitude = longitude
                block_obj.save()

            # Process flat type
            flat_type = room['flat_type']
            flat_type_obj, created = FlatType.objects.get_or_create(
                name=flat_type,
            )

            # Process level
            level = room['level']
            try:
                level = level_options['level']
            except KeyError:
                level = re.search(r'\d+', level).group()
                if level:
                    level = int(level)
                    if level > 13:
                        level = level_options['others']
                    else:
                        level = level_options['undefined']
                else:
                    level = level_options['undefined']

            level_type_obj, created = LevelType.objects.get_or_create(
                storey_range=level,
            )


            # 1 - 3 Very Low
            # 4 - 6 Low
            # 7 - 9 Intermediate
            # 10 - 12 High
            # Higher than 13 Very High
