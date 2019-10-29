# Facebook-page-collector

Collect the post of Facebook page.

This program can collect posts on several Facebook page and output to JSON format, easy for the next step of processing.

Not used multi-thread, because Facebook is very strict to the collection.

## Program parameters

In the `settings.py`:

```Python
# List of id to collect
PAGE_IDS = [
    'PAGE_ID_YOU_WANT_TO_GET_1',
    'PAGE_ID_YOU_WANT_TO_GET_2',
]
COOKIES = 'YOUR_FACEBOOK_COOKIES'
SWITCHS = {
    # Get all the comments of one post or just recent comments, False will be faster
    'get_all_comments': False,
    # Get all the reactions of one post or just first 50, False will be faster, True will got banned
    'get_all_reactions': False,
    # If we remember all the posts we get everytime and do not get it next time
    'remember_got_posts': True
}
# How many posts to get each page, 0 will get all the posts
POSTS_TO_GET_EACH_PAGE = 0

# Every time get how many post from Facebook API
# Maximum 200, more than 200 the Facebook server will return a error
# No need change if no specific problem
NUM_TO_FETCH = 200
# Max retry times
# No need change if no specific problem
MAX_RETRY = 2000000
# Retry sleep in second
# No need change if no specific problem
RETRY_SLEEP = 600
# Prevent block sleep time in second
# No need change if no specific problem
PREVENT_BLOCK_SLEEP_TIME = 120
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
