import requests

from main.utils.BaseAPI import BaseAPI


class OneMapAPI(BaseAPI):
    base_url = "https://developers.onemap.sg/commonapi/search"
    api_name = "One Map API"

    def __init__(self):
        super().__init__()
        if not self.__test_connection():
            raise Exception("Unable to initiate OneMapAPI, API Server down.")

    def __test_connection(self):
        payload = {"searchVal": 'Singapore', "returnGeom": "Y", "getAddrDetails": "N"}
        connection = requests.get(self.base_url, params=payload, timeout=10)
        if connection.status_code == 200:
            return True
        else:
            return False

    def get_coordinates(self, address):
        payload = {
            "searchVal": address,
            "returnGeom": "Y",
            "getAddrDetails": "N",
        }
        try:
            req = requests.get(self.base_url, params=payload, timeout=10)
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
