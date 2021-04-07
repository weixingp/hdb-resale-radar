import datetime
import re

import requests
from django.core.exceptions import ObjectDoesNotExist
from main.models import Town, BlockAddress, FlatType, LevelType, Room
from main.utils.BaseAPI import BaseAPI
from main.utils.OneMapAPI import OneMapAPI
from main.utils.util import get_storey_range


class APIManager(BaseAPI):
    api_name = "HDB API"
    resource_id = '42ff9cfe-abe5-4b54-beda-c88f9bb438ee'  # Resale HDB data ID
    base_url = "https://data.gov.sg/api/action/datastore_search"  # SG Gov Data API
    full_data = []

    def __init__(self):
        super().__init__()
        if not self.__test_connection():
            raise Exception("Unable to initiate APIManager, API Server down.")

    def __test_connection(self):
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
            '13 TO 15': 'Very High',
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

            town_obj, created = Town.objects.get_or_create(name=town)

            # town_obj = Town.objects.filter(name=town)
            # if not town_obj:
            #     town_obj = Town.objects.create(name=town)
            # else:
            #     town_obj = town_obj[0]

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
            flat_type_obj, created = FlatType.objects.get_or_create(name=flat_type)

            # Process level
            level_n = room['storey_range']
            level = get_storey_range(level_n)
            level_type_obj, created = LevelType.objects.get_or_create(storey_range=level)

            # Process Room data
            price = float(room['resale_price'])
            lease = room['remaining_lease']
            area = room['floor_area_sqm']
            room_id = room['_id']
            room_obj = Room.objects.filter(id=room_id)
            try:
                year, date = room['month'].split('-')
                resale_date = datetime.datetime(int(year), int(date), 1)
            except:
                resale_date = None

            if not room_obj:
                Room.objects.create(
                    id=room_id,
                    flat_type=flat_type_obj,
                    level_type=level_type_obj,
                    block_address=block_obj,
                    resale_prices=price,
                    remaining_lease=lease,
                    area=area,
                    resale_date=resale_date,
                )
