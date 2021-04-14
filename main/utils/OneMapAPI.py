import os

import requests
from django.utils.timezone import localtime

from main.utils.BaseAPI import BaseAPI


class OneMapAPI(BaseAPI):
    base_url = "https://developers.onemap.sg"
    api_name = "One Map API"
    # account = os.environ['ONEMAP_account']
    # password = os.environ['ONEMAP_password']
    token = None

    def __init__(self):
        super().__init__()
        if not self.__test_connection():
            raise Exception("Unable to initiate OneMapAPI, API Server down.")

        # self.__set_token()

    # def __set_token(self):
    #     url = self.base_url + "/privateapi/auth/post/getToken"
    #     payload = {"email": self.account, "password": self.password}
    #     res = requests.get(url, params=payload, timeout=10)
    #     self.token = res.json()['access_token']

    def __test_connection(self):
        url = self.base_url + "/commonapi/search"
        payload = {"searchVal": 'Singapore', "returnGeom": "Y", "getAddrDetails": "N"}
        connection = requests.get(url, params=payload, timeout=10)
        if connection.status_code == 200:
            return True
        else:
            return False

    def get_coordinates(self, address):
        url = self.base_url + "/commonapi/search"

        payload = {
            "searchVal": address,
            "returnGeom": "Y",
            "getAddrDetails": "N",
        }
        try:
            req = requests.get(url, params=payload, timeout=10)
            data = req.json()

            if data["results"]:
                res = data["results"][0]
                lat = res['LATITUDE']
                long = res['LONGITUDE']
                return {"lat": lat, "long": long}
            else:
                return None
        except:
            return None
