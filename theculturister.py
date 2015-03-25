import csv
import json
import os
import urllib
import uuid
import shutil

import facebook
import tweepy

import config
import credentials


# AUXLIAR
def skip_lines(reader, n):
    for i in range(n):
        reader.next()

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
    csvfile = open(config.GOOGLE_FACEBOOK_REPORT)
    reader = csv.reader(
        csvfile,
        delimiter=config.CSV_DELIMITER,
        quotechar=config.CSV_QUOTECHAR
    )
    skip_lines(reader, 6)
    reader.next()
    for row in reader:
        if row:
            url = row[0]
            sessions = row[1]
            if url:
                if url.startswith('www'):
                    url = url[4:]
                if not url in facebook_sessions:
                    facebook_sessions[url] = int(sessions)
                else:
                    facebook_sessions[url] += int(sessions)
        else:
            break
    
    # Twitter sessions
    twitter_sessions = {}
    csvfile = open(config.GOOGLE_TWITTER_REPORT)
    reader = csv.reader(
        csvfile,
        delimiter=config.CSV_DELIMITER,
        quotechar=config.CSV_QUOTECHAR
    )
    skip_lines(reader, 6)
    reader.next()
    for row in reader:
        if row:
            url = row[0]
            sessions = row[1]
            if url:
                if url.startswith('www'):
                    url = url[4:]
                if not url in twitter_sessions:
                    twitter_sessions[url] = int(sessions)
                else:
                    twitter_sessions[url] += int(sessions)
        else:
            break
    
    # Pages
    base_url = 'theculturist.ca'
    csvfile = open(config.GOOGLE_PAGES_REPORT)
    reader = csv.reader(
        csvfile,
        delimiter=config.CSV_DELIMITER,
        quotechar=config.CSV_QUOTECHAR
    )
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

# MAIN
def main():
    writers = prepare_sylva()
    process_google(writers)
#    process_facebook(writers)
#    process_twitter(writers)

main()
