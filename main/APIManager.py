import requests


class APIManager:
    resource_id = '42ff9cfe-abe5-4b54-beda-c88f9bb438ee'  # Resale HDB data
    base_url = "https://data.gov.sg/api/action/datastore_search"  # SG Gov Data API

    def __init__(self):
        self.full_data = []

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

