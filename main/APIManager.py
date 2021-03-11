import re
import time

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from main.models import Town, BlockAddress, FlatType, LevelType, Room
from main.utils.OneMapAPI import OneMapAPI


class APIManager:
    resource_id = '42ff9cfe-abe5-4b54-beda-c88f9bb438ee'  # Resale HDB data ID
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

    def load_data(self, order="asc"):
        print("Loading data from data.gov.sg...")
        full_data = []
        total = requests.get(
            self.base_url,
            params={'resource_id': self.resource_id, 'limit': 1}
        ).json()['result']['total']

        limit = 10000
        offset = 0

        while offset < total:
            payload = {
                'resource_id': self.resource_id,
                'limit': limit,
                'offset': offset,
                'sort': "_id " + order
            }
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

    def import_to_database(self, update=False, print_output=False):
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
        count = 0
        if update:
            try:
                last_id = Room.objects.latest('id').id
            except ObjectDoesNotExist:
                last_id = 0
            total = int(self.full_data[0]["_id"]) - last_id

            if total == 0 and print_output:
                print("Nothing to update, exiting...")
        else:
            total = len(self.full_data)
            last_id = 0

        for room in self.full_data:
            if room["_id"] == last_id:
                break
            count += 1

            if print_output:
                print(f"Processing {count} / {total}")

            # Process town data
            town = room['town']

            town_obj = Town.objects.filter(name=town)
            if not town_obj:
                town_obj = Town.objects.create(name=town)
            else:
                town_obj = town_obj[0]

            # Process address data
            block = room['block']
            street_name = room['street_name']

            block_obj = BlockAddress.objects.filter(
                block=block,
                street_name=street_name,
            )

            if not block_obj:
                try:
                    coord = one_map.get_coordinates(block + " " + street_name)
                except Exception as e:
                    coord = None

                if coord:
                    latitude = coord['lat']
                    longitude = coord['long']
                else:
                    latitude = None
                    longitude = None

                block_obj = BlockAddress.objects.create(
                    block=block,
                    street_name=street_name,
                    town_name=town_obj,
                    latitude=latitude,
                    longitude=longitude,
                )
            else:
                block_obj = block_obj[0]
                if not block_obj.latitude or block_obj.longitude:
                    coord = one_map.get_coordinates(block + " " + street_name)
                    if coord:
                        latitude = coord['lat']
                        longitude = coord['long']
                    else:
                        latitude = None
                        longitude = None

                    block_obj.latitude = latitude
                    block_obj.longitude = longitude

            # Process flat type
            flat_type = room['flat_type']

            flat_type_obj = FlatType.objects.filter(name=flat_type)
            if not flat_type_obj:
                flat_type_obj = FlatType.objects.create(
                    name=flat_type
                )
            else:
                flat_type_obj = flat_type_obj[0]

            # Process level
            level = room['storey_range']
            try:
                level = level_options[level]
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

            level_type_obj = LevelType.objects.filter(storey_range=level)
            if not level_type_obj:
                level_type_obj = LevelType.objects.create(storey_range=level)
            else:
                level_type_obj = level_type_obj[0]

            # Process Room data
            price = float(room['resale_price'])
            lease = room['remaining_lease']
            area = room['floor_area_sqm']
            room_id = room['_id']
            room_obj = Room.objects.filter(id=room_id)

            if not room_obj:
                room_obj = Room.objects.create(
                    id=room_id,
                    flat_type=flat_type_obj,
                    level_type=level_type_obj,
                    block_address=block_obj,
                    resale_prices=price,
                    remaining_lease=lease,
                    area=area,
                )
