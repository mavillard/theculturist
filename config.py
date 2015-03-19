import os


# CSV characters
CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))

report_fb_dir = os.path.join(current_dir, 'files', 'reports', 'facebook')
REPORT_FB_FILE = os.path.join(report_fb_dir, 'post_2015-02-17_2015-03-16.csv')

SYLVADB_DIR = os.path.join(current_dir, 'files', 'sylvadb')

# Schema
SCHEMA = {
    'nodes': {
        'user': ['id', 'type', 'Name',],
        'post': ['id', 'type', 'Permalink', 'Message', 'Date', 'Reach',
                 'Engagement', 'NLikes', 'NComments', 'NShares',],
    },
    'rels': {
        'like': ['source id', 'target id', 'label',],
        'comment': ['source id', 'target id', 'label', 'Date',],
#        'share': ['source id', 'target id', 'label', 'Date',],
#        'reach': ['source id', 'target id', 'label', 'Date',],
    }
}
