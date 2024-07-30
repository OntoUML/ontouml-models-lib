from typing import Optional

from model import Model

import requests
from typing import Optional

class OnlineCatalog:
    BASE_URL = "https://api.github.com/repos/OntoUML/ontouml-models/contents/models"

    def __init__(self, token: Optional[str] = None):
        self.token = token

    def list_models_folders(self) -> list[str]:
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.token:
            headers['Authorization'] = f'token {self.token}'

        response = requests.get(self.BASE_URL, headers=headers)
        if response.status_code == 200:
            contents = response.json()
            folders = [item['name'] for item in contents if item['type'] == 'dir']
            return folders
        else:
            raise RuntimeError(f"Failed to fetch repository details: {response.status_code} {response.text}")

    def test_token(self) -> None:
        if not self.token:
            print("No token provided. Skipping token test.")
            return

        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get("https://api.github.com/repos/OntoUML/ontouml-models", headers=headers)
        if response.status_code == 200:
            print("Token works! Repository details fetched successfully.")
        else:
            print(f"Failed to fetch repository details: {response.status_code} {response.text}")

