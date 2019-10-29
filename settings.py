# Settings for Facebook page downloader

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
