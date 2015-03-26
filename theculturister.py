import csv
import json
import os
import re
import urllib
import uuid
import shutil

import facebook
import tweepy

import config
import credentials


# AUXLIAR
article_ids = set()
fb_user_ids = set()
tw_user_ids = set()

def get_report_reader(report):
    csvfile = open(report)
    return csv.reader(
        csvfile,
        delimiter=config.CSV_DELIMITER,
        quotechar=config.CSV_QUOTECHAR
    )

def skip_lines(reader, n):
    for i in range(n):
        reader.next()

def to_ascii(s):
    result = s
    if type(s) != str:
        result = s.encode('utf-8')
    return result

def format_date_fb_csv(date_time):
    date = date_time.split(' ')[0]
    (month, day, year) = map(int, date.split('/'))
    formatted_date = '{}-{}-{}'.format(year, month, day)
    return formatted_date

def format_date_fb_api(date_time):
    date = date_time.split('T')[0]
    (year, month, day) = map(int, date.split('-'))
    formatted_date = '{}-{}-{}'.format(year, month, day)
    return formatted_date

def clean_url(url):
    if url.startswith('https://'):
        url = url[8:]
    if url.startswith('http://'):
        url = url[7:]
    if url.startswith('www.'):
        url = url[4:]
    return url

# SYLVA
def create_csv_writers(schema):
    writers = {}
    for k1 in schema:
        folder = os.path.join(config.SYLVA_DIR, k1)
        os.makedirs(folder)
        
        d = schema[k1]
        for k2 in d:
            filepath = os.path.join(
                config.SYLVA_DIR,
                k1,
                '{}.csv'.format(k2)
            )
            csvfile = open(filepath, 'ab')
            writer = csv.writer(
                csvfile,
                delimiter=config.CSV_DELIMITER,
                quotechar=config.CSV_QUOTECHAR,
                quoting=csv.QUOTE_ALL
            )
            writer.writerow(d[k2])
            writers[k2] = writer
    return writers

def prepare_sylva():
    shutil.rmtree(config.SYLVA_DIR, ignore_errors=True)
    os.makedirs(config.SYLVA_DIR)
    writers = create_csv_writers(config.SCHEMA)
    return writers

# GOOGLE
def create_sessions(writers, article_id, total_views, fb_views, tw_views):
    for i in range(total_views):
        session_id = str(uuid.uuid1())
        session_type = 'Session'
        if 0 <= i < fb_views:
            origin = 'facebook'
        elif fb_views <= i < fb_views + tw_views:
            origin = 'twitter'
        else: #fb_views + tw_views <= i < total_views
            origin = 'other'
        writers['Session'].writerow([session_id, session_type, origin])
        writers['session_visits'].writerow([
            session_id,
            article_id,
            'session_visits'
        ])

def process_google(writers):
    # Website
    TOTAL_USERS = 870
    writers['Website'].writerow([1, 'Website', 'theculturist_ca', TOTAL_USERS])
    
    # Facebook sessions
    facebook_sessions = {}
    reader = get_report_reader(config.GOOGLE_FACEBOOK_REPORT)
    skip_lines(reader, 6)
    reader.next()
    for row in reader:
        if row:
            url = row[0]
            sessions = row[1]
            if url:
                url = clean_url(url)
                if not url in facebook_sessions:
                    facebook_sessions[url] = int(sessions)
                else:
                    facebook_sessions[url] += int(sessions)
        else:
            break
    
    # Twitter sessions
    twitter_sessions = {}
    reader = get_report_reader(config.GOOGLE_TWITTER_REPORT)
    skip_lines(reader, 6)
    reader.next()
    for row in reader:
        if row:
            url = row[0]
            sessions = row[1]
            if url:
                url = clean_url(url)
                if not url in twitter_sessions:
                    twitter_sessions[url] = int(sessions)
                else:
                    twitter_sessions[url] += int(sessions)
        else:
            break
    
    # Articles
    base_url = 'theculturist.ca'
    reader = get_report_reader(config.GOOGLE_PAGES_REPORT)
    skip_lines(reader, 6)
    reader.next()
    for row in reader:
        if row:
            url = row[0]
            total_views = row[1]
            entrances = row[4]
            bounce_rate = row[5]
            if url and '?' not in url:
                # Create the article
                url = '{}{}'.format(base_url, url)
                article_id = url
                article_type = 'Article'
                total_views = int(total_views)
                writers['Article'].writerow([
                    article_id,
                    article_type,
                    bounce_rate,
                    entrances,
                    total_views,
                    url
                ])
                article_ids.add(article_id)
                # Link the article to the website
                writers['article_belongs_to'].writerow([
                    article_id,
                    1,
                    'article_belongs_to'
                ])
                # Create the sessions for the article
                if url in facebook_sessions:
                    facebook_views = facebook_sessions[url]
                else:
                    facebook_views = 0
                if url in twitter_sessions:
                    twitter_views = twitter_sessions[url]
                else:
                    twitter_views = 0
                create_sessions(
                    writers,
                    article_id,
                    total_views,
                    facebook_views,
                    twitter_views
                )
        else:
            break

# FACEBOOK
def process_likers(writers, post_id, likes):
    for like in likes:
        user_id = like['id']
        name = like['name']
        # If the user does not exist create the user
        if user_id not in fb_user_ids:
            user_type = 'FacebookUser'
            name = to_ascii(name)
            writers['FacebookUser'].writerow([user_id, user_type, name])
            fb_user_ids.add(user_id)
        # Create the relation
        writers['fbuser_likes'].writerow([user_id, post_id, 'fbuser_likes'])

def process_commenters(writers, post_id, comments):
    for comment in comments:
        user_id = comment['from']['id']
        name = comment['from']['name']
        date = comment['created_time']
        # If the user does not exist create the user
        if user_id not in fb_user_ids:
            user_type = 'FacebookUser'
            name = to_ascii(name)
            writers['FacebookUser'].writerow([user_id, user_type, name])
            fb_user_ids.add(user_id)
        # Create the relation
#        date = format_date_fb_api(date)
        writers['fbuser_comments'].writerow([
            user_id,
            post_id,
            'fbuser_comments'
            #date
        ])

def process_mentions(writers, post_id, mentions):
    for mention in mentions:
        user_id = mention['id']
        name = mention['name']
        # If the user does not exist create the user
        if user_id not in fb_user_ids:
            user_type = 'FacebookUser'
            name = to_ascii(name)
            writers['FacebookUser'].writerow([user_id, user_type, name])
            fb_user_ids.add(user_id)
        # Create the relation
        writers['post_mentions'].writerow([post_id, user_id, 'post_mentions'])

def extract_urls(text):
    regexp = ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
    urls = re.findall(regexp, text)
    return map(lambda x: x[0], urls)

def process_facebook(writers):
    # Page
    TOTAL_LIKES = 440
    writers['FacebookPage'].writerow([2, 'FacebookPage', 'theculturist_ca', TOTAL_LIKES])
    
    # Posts
    fb_api = facebook.GraphAPI(credentials.FB_ACCESS_TOKEN)
    
    reader = get_report_reader(config.FACEBOOK_POSTS_REPORT)
    reader.next()
    reader.next()
    for row in reader:
        if row:
            post_id = row[0]
            permalink = row[1]
            text = row[2]
            date = row[6]
            reach = row[7]
            engagement = row[13]
            
            post_type = 'Post'
            text = to_ascii(text)
            date = format_date_fb_csv(date)
            
            post = fb_api.get_object(post_id)
            if 'likes' in post:
                data = post['likes']['data']
                likes = len(data)
                # Process the users that liked this post
                process_likers(writers, post_id, data)
            else:
                likes = 0
            if 'comments' in post:
                data = post['comments']['data']
                comments = len(data)
                # Process the users that commented on this post
                process_commenters(writers, post_id, data)
            else:
                comments = 0
            if 'shares' in post:
                shares = post['shares']['count']
            else:
                shares = 0
            
            writers['Post'].writerow([
                post_id,
                post_type,
                comments,
                engagement,
                likes,
                permalink,
                date,
                reach,
                shares,
                text
            ])
            
            # Link the post to the facebook page
            writers['article_belongs_to'].writerow([
                post_id,
                2,
                'post_belongs_to'
            ])
            
            # Link the post to the article
            urls = extract_urls(text)
            for url in urls:
                response = urllib.urlopen(url)
                if response.getcode() == 200:
                    url = clean_url(response.url)
                    if url in article_ids:
                        writers['post_links_to'].writerow([
                            post_id,
                            url,
                            'post_links_to'
                        ])
            
            # Link the post to the mentioned users
            if 'to' in post:
                data = post['to']['data']
                # Process the users mentioned on this post
                process_mentions(writers, post_id, data)
        else:
            break

# TWITTER
def process_twitter(writers):
    # Account
    TOTAL_FOLLOWERS = 415
    writers['TwitterAccount'].writerow([3, 'TwitterAccount', 'theculturist_ca', TOTAL_FOLLOWERS])
    
    # Tweets
    consumer_key = credentials.TW_CONSUMER_KEY
    consumer_secret = credentials.TW_CONSUMER_SECRET
    access_token = credentials.TW_ACCESS_TOKEN
    access_token_secret = credentials.TW_ACCESS_TOKEN_SECRET
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    tw_api = tweepy.API(auth)
    
    reader = get_report_reader(config.TWITTER_TWEETS_REPORT)
    reader.next()
    for row in reader:
        if row:
            tweet_id = row[0]
            permalink = row[1]
            text = row[2]
            date = row[6]
            reach = row[7]
            engagement = row[13]
            
            post_type = 'Post'
            text = to_ascii(text)
            date = format_date_fb_csv(date)
            
            post = fb_api.get_object(post_id)
            if 'likes' in post:
                data = post['likes']['data']
                likes = len(data)
                # Process the users that liked this post
                process_likers(writers, post_id, data)
            else:
                likes = 0
            if 'comments' in post:
                data = post['comments']['data']
                comments = len(data)
                # Process the users that commented on this post
                process_commenters(writers, post_id, data)
            else:
                comments = 0
            if 'shares' in post:
                shares = post['shares']['count']
            else:
                shares = 0
            
            writers['Post'].writerow([
                post_id,
                post_type,
                comments,
                engagement,
                likes,
                permalink,
                date,
                reach,
                shares,
                text
            ])
            
            # Link the post to the facebook page
            writers['article_belongs_to'].writerow([
                post_id,
                2,
                'post_belongs_to'
            ])
            
            # Link the post to the article
            urls = extract_urls(text)
            for url in urls:
                response = urllib.urlopen(url)
                if response.getcode() == 200:
                    url = clean_url(response.url)
                    if url in article_ids:
                        writers['post_links_to'].writerow([
                            post_id,
                            url,
                            'post_links_to'
                        ])
            
            # Link the post to the mentioned users
            if 'to' in post:
                data = post['to']['data']
                # Process the users mentioned on this post
                process_mentions(writers, post_id, data)
        else:
            break


# MAIN
def main():
    writers = prepare_sylva()
    process_google(writers)
    process_facebook(writers)
    process_twitter(writers)

main()
