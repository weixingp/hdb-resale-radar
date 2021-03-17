import requests


class OneMapAPI:
    base_url = "https://developers.onemap.sg/commonapi/search"

    def __init__(self):
        if not self.test_connection():
            raise Exception("Unable to initiate OneMapAPI, API Server down.")

    def test_connection(self):
        payload = {"searchVal": 'Singapore', "returnGeom": "Y", "getAddrDetails": "N"}
        connection = requests.get(self.base_url, params=payload)
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

        req = requests.get(self.base_url, params=payload)
        data = req.json()

        if data["results"]:
            res = data["results"][0]
            lat = res['LATITUDE']
            long = res['LONGITUDE']
            return {"lat": lat, "long": long}
        else:
            return None
