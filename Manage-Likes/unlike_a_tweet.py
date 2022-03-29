#!/usr/bin/env python3
from requests_oauthlib import OAuth1Session
import os
import json
import time
import datetime
import re
import sys

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")

# Be sure to replace your-user-id with your own user ID or one of an authenticated user
# You can find a user ID by using the user lookup endpoint
user_id = 'your-user-id'
sleep_time_second = 20 # Rate Limit for Deleting Likes = 50 Requests per 15 Minutes Window
delete_tweet_first_index = 0
max_search_tweet = 1000
regex_str = 'your-string-to-undo-like-by-regex'
regex_flags = re.I|re.M
json_file = open('like.json', 'r')
json_data = json.load(json_file)

print("Number of Likes: " + str(len(json_data)))
print("Regular Expression: \'" + regex_str + "\'")

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
        print("No Likes Anymore!")
        sys.exit()
    tweet_id = json_data[i]['like']['tweetId']
    like_text = repr(json_data[i]['like']['fullText']) # Make Raw String like r'string'
    if re.search(regex_str, like_text, regex_flags) == None:
        continue
    print("--------------------------------")
    print("Index: " + str(i))
    print("Tweet ID: " + tweet_id)
    print("Full Text: " + like_text)
    print("Waiting for " + str(sleep_time_second) + " Seconds...")
    time.sleep(sleep_time_second)
    # Making the request
    response = oauth.delete("https://api.twitter.com/2/users/{}/likes/{}".format(user_id, tweet_id))

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response Code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    response = json_response['data']['liked']
    #print(json_response)
    print("Liked: " + str(response))
    count_delete += 1
    print("Deleted Likes: " + str(count_delete))

