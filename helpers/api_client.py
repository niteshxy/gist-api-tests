import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class api_client:
    def __init__(self, base_url, access_token=None):
        self.base_url = base_url
        self.headers = {'Accept': 'application/vnd.github+json'}
        if access_token:
            self.headers['Authorization'] = f'token {access_token}'

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        logging.info(f"Sending {method} request to: {url}")
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise

    def create_gist(self, payload):
        return self._request("POST", "/gists", data=payload)

    def get_gist(self, gist_id):
        return self._request("GET", f"/gists/{gist_id}")

    def update_gist(self, gist_id, payload):
        return self._request("PATCH", f"/gists/{gist_id}", data=payload)

    def delete_gist(self, gist_id):
        return self._request("DELETE", f"/gists/{gist_id}")

    def list_public_gists(self):
        return self._request("GET", "/gists/public")

    def list_authenticated_user_gists(self):
        return self._request("GET", "/gists")