import networkx as nx
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
theculturist = api.get_user('theculturist_ca')


# NETWORK
graph = nx.DiGraph()

# Functions
def add_user(user):
    if not graph.has_node(user.id):
        info = {
            'handle': user.screen_name,
            'fullname': user.name,
            'node_type': 'user',
        }
        graph.add_node(user.id, info)

def add_status(status):
    if not graph.has_node(status.id):
        info = {
            'text': status.text,
            'node_type': 'status',
        }
        graph.add_node(status.id, info)

def add_post(user, status):
    if not graph.has_edge(user.id, status.id):
        add_user(user)
        add_status(status)
        info = {
            'datetime': str(status.created_at),
            'edge_type': 'posts',
        }
        graph.add_edge(user.id, status.id, info)

def add_retweet(user, status):
    if not graph.has_edge(user.id, status.id):
        add_user(user)
        add_status(status)
        info = {
            'datetime': str(status.created_at),
            'edge_type': 'retweets',
        }
        graph.add_edge(user.id, status.id, info)

def add_mention(status, user):
    if not graph.has_edge(user.id, status.id):
        add_user(user)
        add_status(status)
        info = {
            'datetime': str(status.created_at),
            'edge_type': 'mentions',
        }
        graph.add_edge(status.id, user.id, info)

def process_retweet(user1, status, user2):
    if user1.screen_name != user2.screen_name:
        add_post(user2, status)
        add_retweet(user1, status)

def process_mention(user1, status, user2):
    if user1.screen_name != user2.screen_name:
        add_post(user1, status)
        add_mention(status, user2)

def process_timeline(user):
    for status in user.timeline():
        for retweet in status.retweets():
            process_retweet(retweet.user, retweet, user)

def process_followers(user):
    for follower in api.followers(user.screen_name):
        for status in follower.timeline():
            for mention in status.entities['user_mentions']:
                if mention['screen_name'] == user.screen_name:
                    process_mention(follower, status, user)


# RESULTS
process_timeline(theculturist)
process_followers(theculturist)
nx.write_gexf(graph, 'theculturist.gexf')



attrs={'type': 1, 'node_type': 2, 'NodeType': 3, 'nodeType': 4, 'Type': 5, 'nodetype': 6}

