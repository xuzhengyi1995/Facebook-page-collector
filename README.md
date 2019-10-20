# Facebook-page-collector

Collect the post of Facebook page.

This program can collect posts on several Facebook page and output to JSON format, easy for the next step of processing.

Not used multi-thread, because Facebook is very strict to the collection.

## Program parameters

```Python
# List of id to collect
PAGE_IDS = [
    'PAGE_ID_YOU_WANT_TO_GET_1',
    'PAGE_ID_YOU_WANT_TO_GET_2',
]
COOKIES = 'YOUR_FACEBOOK_COOKIES'
# How many posts to get once time, TRIED MAXIMUM 200
NUM_TO_FETCH = 200
# If account has been temporarily blocked, max retry time
MAX_RETRY = 20
# Retry sleep in second
RETRY_SLEEP = 300
# Prevent block sleep time
PREVENT_BLOCK_SLEEP_TIME = 5
```

## How to run the program

1.  Write your own parameters as above.
2.  run `python fb_downloader.py` in shell.

## Output data structure

Output data will be in format JSON.

The program will create a folder like `YYYYMMDD-HHMMSS` like `20191020-215658`, and will create the sub-folder with the page id like `222778774519430`, in the sub-folder, each post will be saved in a JSON file begin with `fbid_` and then its post id like `fbid_1675338865930073.json`.

The output JSON data will be like this:

```json
{
  "page_id": "THE ID OF THE PAGE",
  "story_fbid": "THE ID OF THIS POST",
  "post_time": "POST TIME",
  "share_count": "SHARE COUNT",
  "post_html": "POST CONTENT IN HTML FORMAT",
  "post_text": "POST CONTENT IN PURE TEXT",
  "comment": {
    "count": "POST COMMENT COUNT (INTEGER)",
    "all_comments": [
      {
        "user_url": "USER URL OF THIS COMMENT",
        "user_name": "USER NAME",
        "comment_html": "COMMENT CONTENT IN HTML FORMAT",
        "comment_text": "COMMENT CONTENT IN PURE TEXT"
      }
    ]
  },
  "reaction": {
    "count": {
      "sum": 105,
      "like": 1,
      "love": 94,
      "haha": 4,
      "wow": 3,
      "angry": 3
    },
    "users_detail": [
      {
        "user_url": "USER URL OF THIS REACTION",
        "user_name": "USER NAME",
        "reaction": "REACTION (like, love, wow, haha, heartbreak, angry)"
      }
    ]
  }
}
```

One example:

```json
{
  "page_id": "222778774519430",
  "story_fbid": "1675338865930073",
  "post_time": "17 hrs",
  "share_count": "1",
  "post_html": "<div class=\"story_body_container\">...</div>",
  "post_text": "Ne vous ... Ils m\u00e9ritent tout notre soutien, toute notre solidarit\u00e9 !",
  "comment": {
    "count": 28,
    "all_comments": [
      {
        "user_url": "xxx?fref=nf&rc=p&refid=52&__tn__=R",
        "user_name": "xxxyyy",
        "comment_html": "Soutien. Ceux qui vivent sont ceux qui luttent.",
        "comment_text": "Soutien. Ceux qui vivent sont ceux qui luttent."
      }
    ]
  },
  "reaction": {
    "count": {
      "sum": 105,
      "like": 1,
      "love": 94,
      "haha": 4,
      "wow": 3,
      "angry": 3
    },
    "users_detail": [
      {
        "user_url": "xxxx/?fref=pb",
        "user_name": "xxxyyy",
        "reaction": "like"
      }
    ]
  }
}
```
