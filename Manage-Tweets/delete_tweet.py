#!/usr/bin/env python3
from requests_oauthlib import OAuth1Session
import os
import json
import time
import datetime
import sys

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
sleep_time_second = 20 # Rate Limit for Deleting Tweets = 50 Requests per 15 Minutes Window
delete_tweet_first_index = 0
max_search_tweet = 1000
min_date_iso8601_str = '2000-01-01'
max_date_iso8601_str = '2021-12-31'
json_file = open('tweet.json', 'r')
min_date_iso8601_data = datetime.date.fromisoformat(min_date_iso8601_str) # New in 3.7
max_date_iso8601_data = datetime.date.fromisoformat(max_date_iso8601_str) # New in 3.7
json_data = json.load(json_file)

print("Number of Tweets: " + str(len(json_data)))
print("Minimum Date of Tweets to Be Deleted: " + str(min_date_iso8601_data))
print("Maximum Date of Tweets to Be Deleted: " + str(max_date_iso8601_data))

# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

# Make the request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

count_delete = 0

for i in range(delete_tweet_first_index, delete_tweet_first_index + max_search_tweet):
    if i >= len(json_data):
        print("No Tweets Anymore!")
        sys.exit()
    # Be sure to replace tweet-id-to-delete with the id of the Tweet you wish to delete. The authenticated user must own the list in order to delete
    id = json_data[i]['tweet']['id']
    date_time_str = json_data[i]['tweet']['created_at']
    date_time_data = datetime.datetime.strptime(date_time_str, '%a %b %d %H:%M:%S %z %Y')
    print("--------------------------------")
    print("Index: " + str(i))
    print("ID: " + id)
    print("Created at: " + date_time_str)
    #print("ISO 8601 Format: " + date_time_data.isoformat('T'))
    if date_time_data.date() < min_date_iso8601_data or date_time_data.date() > max_date_iso8601_data:
        print("Tweet date is not in the range!")
        continue
    print("Full Text: " + json_data[i]['tweet']['full_text'])
    print("Waiting for " + str(sleep_time_second) + " Seconds...")
    time.sleep(sleep_time_second)
    # Making the request
    response = oauth.delete("https://api.twitter.com/2/tweets/{}".format(id))

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response Code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    response = json_response['data']['deleted']
    #print(json_response)
    print("Deleted: " + str(response))
    count_delete += 1
    print("Deleted Tweets: " + str(count_delete))

