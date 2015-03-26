import os


# CSV characters
CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
reports_dir = os.path.join(current_dir, 'files', 'reports')
google_dir = os.path.join(reports_dir, 'google')
GOOGLE_PAGES_REPORT = os.path.join(google_dir, 'pages.csv')
GOOGLE_FACEBOOK_REPORT = os.path.join(google_dir, 'facebook.csv')
GOOGLE_TWITTER_REPORT = os.path.join(google_dir, 'twitter.csv')
facebook_dir = os.path.join(reports_dir, 'facebook')
FACEBOOK_PAGE_REPORT = os.path.join(facebook_dir, 'page.csv')
FACEBOOK_POSTS_REPORT = os.path.join(facebook_dir, 'posts.csv')
twitter_dir = os.path.join(reports_dir, 'twitter')
TWITTER_TWEETS_REPORT = os.path.join(twitter_dir, 'tweets.csv')
SYLVA_DIR = os.path.join(current_dir, 'files', 'sylva')
SYLVA_DIR_NODES = os.path.join(SYLVA_DIR, 'nodes')
SYLVA_DIR_RELATIONS = os.path.join(SYLVA_DIR, 'relations')

# Schema
SCHEMA = {
    'nodes': {
        'Article': ['id', 'type', 'bounce_rate', 'entrances', 'total_views', 'url'],
        'FacebookPage': ['id', 'type', 'name', 'total_likes'],
        'FacebookUser': ['id', 'type', 'name'],
        'Post': ['id', 'type', 'comments', 'date', 'engagement', 'likes', 'permalink', 'reach', 'shares', 'text'],
        'Session': ['id', 'type', 'origin'],
        'Tweet': ['id', 'type', 'date', 'engagement', 'favorites', 'hashtags', 'impression', 'permalink', 'replies', 'retweets', 'text'],
        'TwitterAccount': ['id', 'type', 'name', 'total_followers'],
        'TwitterUser': ['id', 'type', 'handle', 'name'],
        'Website': ['id', 'type', 'name', 'total_users'],
    },
    'relations': {
        'article_belongs_to': ['source id', 'target id', 'label'],
        'fb_related_to': ['source id', 'target id', 'label'],
        'fbuser_comments': ['source id', 'target id', 'label'], #date
        'fbuser_likes': ['source id', 'target id', 'label'],
        'post_belongs_to': ['source id', 'target id', 'label'],
        'post_links_to': ['source id', 'target id', 'label'],
        'post_mentions': ['source id', 'target id', 'label'],
        'session_visits': ['source id', 'target id', 'label'],
        'tw_related_to': ['source id', 'target id', 'label'],
        'tweet_belongs_to': ['source id', 'target id', 'label'],
        'tweet_links_to': ['source id', 'target id', 'label'],
        'tweet_mentions': ['source id', 'target id', 'label'],
        'twuser_retweets': ['source id', 'target id', 'label'], #date
    }
}
