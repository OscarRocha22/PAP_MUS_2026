import json
from pathlib import Path

import pandas as pd

# Paths
ROOT_DIR = Path(__file__).resolve().parent
RAW_PATH = ROOT_DIR / "data" / "raw" / "facebook_3months.json"      # .json (array) or .jsonl/.ndjson
CLEAN_PATH = ROOT_DIR / "data" / "clean" / "facebook_3months.csv"

# Column mapping: JSON path -> clean column name.
# Paths use "/" between keys and numeric segments to index into lists,
# so these are the same names you used with the CSV export.
MAPPING_COLS = {
    "url": "url",
    "user/name": "author_name",
    "topComments/1/author/gender": "author_gender",
    "attachments/0/photo_image/uri": "photo_url",
    "text": "text",
    "time": "time",
    "reactionAngryCount": "angry_count",
    "reactionCareCount": "hug_count",
    "reactionHahaCount": "laugh_count",
    "reactionLikeCount": "like_count",
    "reactionLoveCount": "love_count",
    "reactionSadCount": "sad_count",
    "reactionWowCount": "surprised_count",
    "sharedPost/text": "shared_post_text",
    "topComments/0/author/name": "top_comment_name",
    "topComments/0/author/gender": "top_comment_gender",
    "topComments/0/text": "top_comment_text",
}

# The scraper omits reaction keys when the count is 0, so absent = 0.
COUNT_COLS = [
    "angry_count", "hug_count", "laugh_count", "like_count",
    "love_count", "sad_count", "surprised_count",
]


def get_path(record, path, default=None):
    """Walk a nested dict/list structure using a 'a/b/0/c' style path.

    Returns `default` if any key is missing, any list index is out of range,
    or an intermediate value is null (e.g. a post with no comments).
    """
    current = record
    for key in path.split("/"):
        if isinstance(current, dict):
            if key not in current:
                return default
            current = current[key]
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                return default
        else:  # None or a scalar before the path ends
            return default
    return current


def iter_records(path):
    """Yield one post (dict) at a time from a .json array or a .jsonl file."""
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        if path.suffix.lower() in {".jsonl", ".ndjson"}:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
        else:
            data = json.load(f)
            yield from ([data] if isinstance(data, dict) else data)


def clean_records(records):
    """Extract only the mapped fields from each raw post -> clean DataFrame."""
    rows = [
        {new: get_path(rec, old) for old, new in MAPPING_COLS.items()}
        for rec in records
    ]
    df = pd.DataFrame(rows, columns=list(MAPPING_COLS.values()))

    df[COUNT_COLS] = df[COUNT_COLS].fillna(0).astype("Int64")
    return df


def main():
    df_clean = clean_records(iter_records(RAW_PATH))

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(CLEAN_PATH, index=False)
    print(f"Dataset cleaned successfully! {len(df_clean)} rows -> {CLEAN_PATH}")


if __name__ == "__main__":
    main()