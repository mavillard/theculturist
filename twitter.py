import tweepy

import credentials


# AUTHENTICATION
consumer_key = credentials.t_consumer_key
consumer_secret = credentials.t_consumer_secret
access_token = credentials.t_access_token
access_token_secret = credentials.t_access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


# API
api = tweepy.API(auth)


# EXAMPLES
# Followers
for f in api.followers('theculturist_ca'):
    print 'Handle: @' + f.screen_name
    print 'Full name: ' + f.name
    print '====================================='



