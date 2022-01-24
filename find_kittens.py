import os
import time

import pandas as pd
from dotenv import load_dotenv
from twilio.base import values
from twilio.rest import Client

from exceptions import FetchError
from kitten_finder import KittenFinder


if __name__ == "__main__":
    # Load in our secret environment variables.
    load_dotenv()

    # Set up my twilio credentials.
    twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
    twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_client = Client(twilio_account_sid, twilio_auth_token)

    # Initialize our kitten finder class.
    kf = KittenFinder()

    try:
        while True:
            # Scrape the petfinder API.
            # If it doesn't return a successful response, wait a few minutes and try again.
            try:
                available_kittens_df = kf.fetch_data()
            except FetchError as e:
                print(e)
                time.sleep(300)
                continue

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
            else:
                print("No new kittens yet! Try again later.")

            # After all is said and done, take a quick break and then try it again!
            time.sleep(300)

    # If anything goes wrong, try to text me and then end the script.
    # I know that wrapping everything in one giant try/except is bad,
    # but this is a simple script for a simple task!
    except Exception:
        twilio_client.messages.create(
            body="The kitten finder got all tangled up! Come help!",
            from_=os.environ['MY_TWILIO_NUMBER'],
            to=os.environ['MY_CELL_NUMBER'],
        )
        raise
