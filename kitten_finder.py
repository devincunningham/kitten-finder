import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv


class KittenFinder:
    def __init__(self):
        self._authorization_header = None
        self._last_authorization = None
        self._task = None

    def fetch_data(self) -> pd.DataFrame:
        """Get all adoptable kittens near me as a dataframe."""
        response = requests.get(
            url='https://api.petfinder.com/v2/animals',
            headers=self.auth_header,
            params={
                'type': 'cat',
                'breed': 'Maine Coon,Domestic Medium Hair,Domestic Long Hair',
                'location': 'Seattle, Washington',
                'distance': 200,
                'age': 'baby, young',
            },
        )
        df = pd.DataFrame(response.json()['animals'])
        df.set_index('id', inplace=True)
        return df

    @staticmethod
    def get_petfinder_authorization_header() -> dict:
        """Get a new authorization header from petfinder."""

        # Send keys to petfinder to get my token.
        response = requests.post(
            url='https://api.petfinder.com/v2/oauth2/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': os.environ['PETFINDER_API_KEY'],
                'client_secret': os.environ['PETFINDER_SECRET_KEY'],
            },
        )

        # Process the response into a header I can use for get requests.
        token_type = response.json()['token_type']
        access_token = response.json()['access_token']
        header = {'Authorization': f'{token_type} {access_token}'}
        return header

    @property
    def auth_header(self) -> dict:
        """Get a new authorization header if necessary or return an existing valid one."""
        if self._last_authorization is None or self._last_authorization < time.time() - 3600:
            self._last_authorization = time.time()
            self._authorization_header = self.get_petfinder_authorization_header()
        return self._authorization_header
