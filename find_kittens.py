import os

import requests
from dotenv import load_dotenv
from twilio.rest import Client


load_dotenv()

data = {
  'grant_type': 'client_credentials',
  'client_id': os.environ['PETFINDER_API_KEY'],
  'client_secret': os.environ['PETFINDER_SECRET_KEY']
}

login_response = requests.post('https://api.petfinder.com/v2/oauth2/token', data=data)
token_type = login_response.json()['token_type']
access_token = login_response.json()['access_token']

headers = {'Authorization': f'{token_type} {access_token}'}
params = {
  'type': 'cat',
  'breed': 'Maine Coon,Domestic Medium Hair,Domestic Long Hair',
  'location': 'Seattle, Washington',
  'distance': 200,
  'age': 'baby, young',
}

query_response = requests.get('https://api.petfinder.com/v2/animals', headers=headers, params=params)
for x in query_response.json()['animals']:
    print(x['url'])

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

# message = client.messages.create(
#     body=x['url'],
#     from_='+16075368813',
#     media_url=[x['photos'][0]['medium']],
#     to='+16693428380',
# )
