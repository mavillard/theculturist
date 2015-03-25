import csv
import json
import os
import shutil

import facebook

import credentials
import config


# ID
#tc_id = '961145843920284'

# MAIN
user_ids = set()

def main():
    shutil.rmtree(config.SYLVADB_DIR, ignore_errors=True)
    os.makedirs(config.SYLVADB_DIR)
    
    writers = create_writers(config.SCHEMA)
    fb = facebook.GraphAPI(credentials.FB_ACCESS_TOKEN)
    
    csvfile = open(config.REPORT_FB_FILE)
    reader = csv.reader(
        csvfile,
        delimiter=config.CSV_DELIMITER,
        quotechar=config.CSV_QUOTECHAR
    )
    reader.next()
    reader.next()
    for row in reader:
        post_id = row[0]
        permalink = row[1]
        message = to_str(row[2])
        date = format_date1(row[6])
        reach = row[7]
        engagement = row[13]
        
        post = fb.get_object(post_id)
        if 'likes' in post:
            data = post['likes']['data']
            nlikes = len(data)
            process_likers(writers, post_id, data)
        else:
            nlikes = 0
        if 'comments' in post:
            data = post['comments']['data']
            ncomments = len(data)
            process_commenters(writers, post_id, data)
        else:
            ncomments = 0
        if 'shares' in post:
            nshares = post['shares']['count']
        else:
            nshares = 0
        
        write_node_post(
            writers['post'],
            post_id,
            permalink,
            message,
            date,
            reach,
            engagement,
            nlikes,
            nshares,
            ncomments
        )

def process_likers(writers, post_id, likes):
    for like in likes:
        user_id = like['id']
        name = to_str(like['name'])
        
        write_node_user(writers['user'], user_id, name)
        write_rel_like(writers['like'], user_id, post_id)

def process_commenters(writers, post_id, comments):
    for comment in comments:
        user_id = comment['from']['id']
        name = to_str(comment['from']['name'])
        date = format_date2(comment['created_time'])
        
        write_node_user(writers['user'], user_id, name)
        write_rel_comment(writers['comment'], user_id, post_id, date)

def format_date1(date_time):
    date = date_time.split(' ')[0]
    (month, day, year) = map(int, date.split('/'))
    formatted_date = '{}-{}-{}'.format(year, month, day)
    return formatted_date

def format_date2(date_time):
    date = date_time.split('T')[0]
    (year, month, day) = map(int, date.split('-'))
    formatted_date = '{}-{}-{}'.format(year, month, day)
    return formatted_date

def create_writers(schema):
    writers = {}
    for k1 in schema:
        folder1 = os.path.join(config.SYLVADB_DIR, k1)
        os.makedirs(folder1)
        
        d = schema[k1]
        for k2 in d:
            filepath = os.path.join(
                config.SYLVADB_DIR,
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

def write_node_user(writer, user_id, name):
    if user_id not in user_ids:
        writer.writerow([user_id, 'User', name])
        user_ids.add(user_id)

def write_node_post(
        writer,
        post_id,
        permalink,
        message,
        date,
        reach,
        engagement,
        nlikes,
        nshares,
        ncomments
    ):
    writer.writerow([
        post_id,
        'Post',
        permalink,
        message,
        date,
        reach,
        engagement,
        nlikes,
        nshares,
        ncomments
    ])

def write_rel_like(writer, user_id, post_id):
    writer.writerow([user_id, post_id, 'like'])

def write_rel_comment(writer, user_id, post_id, date):
    writer.writerow([user_id, post_id, 'comment', date])

def to_str(s):
    result = s
    if type(s) != str:
        result = s.encode('utf-8')
    return result

main()
