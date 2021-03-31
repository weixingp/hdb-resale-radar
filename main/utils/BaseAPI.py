import requests


class BaseAPI:
    base_url = None
    api_name = "Unknown"

    def __init__(self):
        pass

    def __test_connection(self):
        res = requests.get(self.base_url)
        if res.status_code == 200:
            return True
        else:
            raise Exception(f"{self.api_name} API Down")