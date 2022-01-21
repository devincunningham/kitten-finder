import asyncio
import os

import requests
from dotenv import load_dotenv


class KittenFinder:
    def __init__(self):
        load_dotenv()
        self.is_started = False
        self._task = None

    async def start(self):
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.ensure_future(self.fetch_data())

    async def fetch_data(self):
        while True:
            auth_header = self.get_petfinder_authorization_header()
            response = requests.get(
                url='https://api.petfinder.com/v2/animals',
                headers=auth_header,
                params={
                    'type': 'cat',
                    'breed': 'Maine Coon,Domestic Medium Hair,Domestic Long Hair',
                    'location': 'Seattle, Washington',
                    'distance': 200,
                    'age': 'baby, young',
                },
            )
            for x in response.json()['animals']:
                print(x['url'])
            await asyncio.sleep(15)

    @staticmethod
    def get_petfinder_authorization_header() -> dict:
        response = requests.post(
            url='https://api.petfinder.com/v2/oauth2/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': os.environ['PETFINDER_API_KEY'],
                'client_secret': os.environ['PETFINDER_SECRET_KEY']
            },
        )

        token_type = response.json()['token_type']
        access_token = response.json()['access_token']
        header = {'Authorization': f'{token_type} {access_token}'}

        return header
