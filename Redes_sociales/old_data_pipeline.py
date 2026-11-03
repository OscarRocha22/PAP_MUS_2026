import pandas as pd
import os

# Get root dir
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load raw df
df = pd.read_csv(ROOT_DIR + '/data/raw/facebook2.csv')

def clean_df(df):
    # Dictionary for column mapping
    MAPPING_COLS = {
        'url': 'url',
        'user/name': 'author_name',
        'topComments/1/author/gender': 'author_gender',
        'attachments/0/photo_image/uri': 'photo_url',
        'text': 'text',
        'time': 'time',
        'reactionAngryCount': 'angry_count',
        'reactionCareCount': 'hug_count',
        'reactionHahaCount': 'laugh_count',
        'reactionLikeCount': 'like_count',
        'reactionLoveCount': 'love_count',
        'reactionSadCount': 'sad_count',
        'reactionWowCount': 'surprised_count',
        'sharedPost/text': 'shared_post_text',
        'topComments/0/author/name': 'top_comment_name',
        'topComments/0/author/gender': 'top_comment_gender',
        'topComments/0/text': 'top_comment_text',
    }

    # Clean df
    df_clean = df[list(MAPPING_COLS.keys())].rename(
        columns=MAPPING_COLS
    )

    # Store df
    df_clean.to_csv(ROOT_DIR + '/data/clean/facebook1.csv')

    return print('Dataset cleaned successfully!')
    

clean_df(df)