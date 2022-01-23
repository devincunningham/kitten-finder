import os
import time

import pandas as pd
from dotenv import load_dotenv
from twilio.base import values
from twilio.rest import Client

from kitten_finder import KittenFinder


if __name__ == "__main__":
    load_dotenv()
    twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
    twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
    kf = KittenFinder()

    while True:
        # Scrape petfinder.
        available_kittens_df = kf.fetch_data()

        # Read in the previously scraped data.
        historical_kittens_df = pd.read_csv('historical_kittens.csv', index_col='id')

        # Compare the newly scraped data with the previously scraped data.
        merged_df = available_kittens_df.merge(historical_kittens_df, on='id', how='outer', indicator=True)
        new_kitten_ids = merged_df[merged_df['_merge'] == 'left_only'].index
        new_kittens_df = available_kittens_df.loc[new_kitten_ids]

        # Overwrite the old csv with the newly scraped data. Out with the old, in with the new!
        available_kittens_df.to_csv('historical_kittens.csv', index=True)

        # If there were any new kittens, text me!
        if not new_kittens_df.empty:
            for _, kitten in new_kittens_df.iterrows():

                # Craft a message.
                if kitten['breeds']['secondary']:
                    kitten_breed = f"{kitten['breeds']['primary']}/{kitten['breeds']['secondary']}".lower()
                else:
                    kitten_breed = kitten['breeds']['primary'].lower()
                kitten_gender = kitten['gender'].lower()
                kitten_name = kitten['name']
                if kitten['primary_photo_cropped']:
                    kitten_photo = kitten['primary_photo_cropped']['full']
                else:
                    kitten_photo = values.unset
                kitten_url = kitten['url']
                message = "New kitten available for adoption: " \
                          f"a {kitten_gender} {kitten_breed} named {kitten_name}! \n{kitten_url}"

                print(message)
                # Text the message to my phone.
                twilio_client.messages.create(
                    body=message,
                    from_=os.environ['MY_TWILIO_NUMBER'],
                    media_url=kitten_photo,
                    to=os.environ['MY_CELL_NUMBER'])

                # A short sleep to protect against my Twilio trial data limits.
                time.sleep(5)

        # After all is said and done, take a quick break and then try it again!
        time.sleep(60)
