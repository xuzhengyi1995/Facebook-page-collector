# Download Facebook page, XU Zhengyi, 28/09/2019

import gzip
import json
import os
import pickle
import random
import re
import signal
import time
from html.parser import HTMLParser
from urllib.parse import quote, unquote

import settings
from get_html import GetHtml

random.seed()
execution_time = time.strftime("%Y%m%d-%H%M%S")
if(os.path.isdir(execution_time) != True):
    os.makedirs(execution_time)
os.makedirs(execution_time + '/errors')

# Load history
if os.path.isfile('./saves.pickle'):
    with open('./saves.pickle', 'rb') as save_file:
        POST_GOT = pickle.load(save_file)
else:
    POST_GOT = {}

# List of id to collect
PAGE_IDS = settings.PAGE_IDS
COOKIES = settings.COOKIES
NUM_TO_FETCH = settings.NUM_TO_FETCH
MAX_RETRY = settings.MAX_RETRY
# Retry sleep in second
RETRY_SLEEP = settings.RETRY_SLEEP
# Prevent block sleep time
PREVENT_BLOCK_SLEEP_TIME = settings.PREVENT_BLOCK_SLEEP_TIME
GET_ALL_COMMENTS = settings.SWITCHS['get_all_comments']
GET_ALL_REACTIONS = settings.SWITCHS['get_all_reactions']
USE_REMEMBER = settings.SWITCHS['remember_got_posts']
POSTS_TO_GET_EACH_PAGE = settings.POSTS_TO_GET_EACH_PAGE
if POSTS_TO_GET_EACH_PAGE != 0 and POSTS_TO_GET_EACH_PAGE < NUM_TO_FETCH:
    NUM_TO_FETCH = POSTS_TO_GET_EACH_PAGE
SUM_POSTS = 0

HEADERS = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': COOKIES,
    'dnt': '1',
    'origin': 'https://m.facebook.com',
    'referer': 'https://m.facebook.com',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'x-requested-with': 'XMLHttpRequest',
    'x-response-format': 'JSONStream'
}
BASE_URL = "https://m.facebook.com/page_content_list_view/more/?page_id=%s&start_cursor=%s&num_to_fetch=%d&surface_type=posts_tab"
STORY_BASE_URL = "https://m.facebook.com/story.php?story_fbid=%s&id=%s"
REACTION_BASE_URL = "https://m.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier=%s&refid=%s"
PREVENT_BLOCK_URLS = [
    'https://m.facebook.com',
    'https://m.facebook.com/Test-118655852867596/?ref=bookmarks',
    'https://m.facebook.com/profile.php',
    'https://m.facebook.com/LegendofZelda/',
    'https://m.facebook.com/groups/816696775067410?group_view_referrer=profile_browser',
    'https://m.facebook.com/Killlakillusa/',
    'https://m.facebook.com/story.php?story_fbid=1320631231435646&id=200999896732124&_ft_=mf_story_key.1320631231435646%3Atop_level_post_id.1320631231435646%3Atl_objid.1320631231435646%3Acontent_owner_id_new.200999896732124%3Athrowback_story_fbid.1320631231435646%3Apage_id.200999896732124%3Aphoto_id.1320618158103620%3Astory_location.4%3Astory_attachment_style.photo%3Apage_insights.%7B%22200999896732124%22%3A%7B%22page_id%22%3A200999896732124%2C%22actor_id%22%3A200999896732124%2C%22dm%22%3A%7B%22isShare%22%3A0%2C%22originalPostOwnerID%22%3A0%7D%2C%22psn%22%3A%22EntStatusCreationStory%22%2C%22post_context%22%3A%7B%22object_fbtype%22%3A266%2C%22publish_time%22%3A1565024400%2C%22story_name%22%3A%22EntStatusCreationStory%22%2C%22story_fbid%22%3A%5B1320631231435646%5D%7D%2C%22role%22%3A1%2C%22sl%22%3A4%2C%22targets%22%3A%5B%7B%22actor_id%22%3A200999896732124%2C%22page_id%22%3A200999896732124%2C%22post_id%22%3A1320631231435646%2C%22role%22%3A1%2C%22share_id%22%3A0%7D%5D%7D%2C%22202514449799345%22%3A%7B%22page_id%22%3A202514449799345%2C%22actor_id%22%3A200999896732124%2C%22dm%22%3A%7B%22isShare%22%3A0%2C%22originalPostOwnerID%22%3A0%7D%2C%22psn%22%3A%22EntStatusCreationStory%22%2C%22role%22%3A16%2C%22sl%22%3A4%7D%7D&__tn__=%2As%2As-R',
    'https://m.facebook.com/LegendofZeldaFrance/photos/a.508106655994144/1505688912902575/?type=3&source=48',
    'https://m.facebook.com/story.php?story_fbid=1491451264326340&id=503423709795772'
]
LEN_PB_URLS = len(PREVENT_BLOCK_URLS)
START_CURSOR_BASE = {
    "timeline_cursor": None,
    "timeline_section_cursor": None,
    "has_next_page": True
}
HTML_PARSER = HTMLParser()
GET_TEXT_RE = re.compile(r'<[^>]*>')
DELETE_SPACE_RE = re.compile(r' {2,}')


def exit_with_save(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    save_history()
    exit()
    signal.signal(signal.SIGINT, exit_with_save)


def save_history():
    with open('./saves.pickle', 'wb') as file_to_save:
        pickle.dump(POST_GOT, file_to_save)


def random_access_pages():
    get_html = GetHtml()
    choosed_url = PREVENT_BLOCK_URLS[int(random.random() * LEN_PB_URLS)]
    get_html.set(url=choosed_url, header=HEADERS)
    get_html.get()


def find_nex_start_cursor(json_require):
    for i in json_require:
        if i[0] == 'InitMMoreItemAutomatic':
            next_url = unquote(i[3][0]['href'])
            return json.loads(next_url.split('start_cursor=')[1].split('&')[0])
    return None


def download_pages():
    global SUM_POSTS
    get_html = GetHtml()
    find_id_re = re.compile(r"story_fbid=([0-9]+)&amp;id=([0-9]+)")
    for page_id in PAGE_IDS:
        SUM_POSTS = 0
        store_folder = execution_time + '/' + page_id
        os.mkdir(store_folder)
        start_cursor = START_CURSOR_BASE
        has_next_page = True
        nb_time = 0
        print('Getting page id: %s' % page_id)
        while has_next_page:
            story_fbid = {}
            nb_time += 1
            print('    Now count: %d' % nb_time)
            this_url = BASE_URL % (page_id, quote(
                json.dumps(start_cursor)), NUM_TO_FETCH)

            get_html.set(url=this_url, header=HEADERS)

            retry_count = 0
            success = False
            while (retry_count < MAX_RETRY) and (not success):
                try:
                    data = gzip.decompress(get_html.get(method='GET'))[9:]
                except:
                    data = get_html.get(method='GET')[9:]
                try:
                    json_data = json.loads(data)
                    success = True
                except:
                    print(
                        '     [PAGES]Facebook has found there is some problem, wait sometime to retry...')
                    retry_count += 1
                    error_file_name = execution_time + '/errors/pages_' + \
                        time.strftime("%Y%m%d-%H%M%S") + \
                        '_' + page_id + '.html'
                    with open(error_file_name, 'w', encoding='utf-8') as file:
                        file.write(data.decode('utf-8'))
                    for _ in range(5):
                        random_access_pages()
                        time.sleep(5)
                    time.sleep(RETRY_SLEEP * retry_count)

            html_post = json_data['payload']['actions'][0]['html']
            js_data = json.loads(
                json_data['payload']['actions'][2]['code'][37:-2])
            require_json = js_data['require']
            start_cursor = find_nex_start_cursor(require_json)
            if start_cursor is None:
                break
            has_next_page = start_cursor['has_next_page']
            # Process html_post
            found_ids = find_id_re.findall(html_post)
            got_count = 0
            for post in found_ids:
                if story_fbid.get(post[0]) is None:
                    story_fbid[post[0]] = post[1]
                    got_count += 1
            print(
                '        This time got %d post ids, start getting detail content...' % got_count)
            download_details(story_fbid, store_folder)
            if POSTS_TO_GET_EACH_PAGE != 0 and SUM_POSTS >= POSTS_TO_GET_EACH_PAGE:
                has_next_page = False


def download_details(ids, store_folder):
    global SUM_POSTS
    get_html = GetHtml()
    '''
    Comment:
        $1: user facebook name
        $2: user name
        $3: comment content
    '''
    get_comment_re = re.compile(
        r'_2b05"><a href="/(.*?)">>?(.*?)</a></div><div data-commentid=".*?>(.*?)</div>')
    get_comment_user_2_re = re.compile(r'<div.*?</div>(.*)')
    get_more_comment_url = re.compile(
        r'data-ajaxify-href="(/ajax/ufi.php\?.*?)"')
    '''
    Reaction url:
        $1: ft_ent_identifier
        $2: refid
    '''
    get_reaction_list_url_re = re.compile(
        r'<a href="/ufi/reaction/profile/browser/\?ft_ent_identifier=([0-9]+)&amp;refid=([0-9]+)"')
    '''
    Share count
    '''
    get_share_count_re = re.compile(
        r'<span data-sigil="feed-ufi-sharers">([0-9]+)')
    '''
    Post content:
        This will be a html block.
        It will contain the time (maybe in chinese).
    '''
    get_post_content_re = re.compile(
        r'(<div class="story_body_container">.*?</div>)<footer')
    get_post_content_text_re = re.compile(
        r'<div class="_5rgt _5nk5"[^>]*>(.*?)</?div')
    get_post_time_re = re.compile(r'<abbr>(.*?)</abbr>')
    for (id1, id2) in ids.items():
        # if we already have this post id or not
        if USE_REMEMBER and POST_GOT.get(id1):
            print('         We have got post id %s, skiped.' % id1)
            continue
        print('         Getting detail info for post id %s' % id1)
        # This page can also be blocked
        post_retry_count = 0
        post_success = False
        while (post_retry_count < MAX_RETRY) and (not post_success):
            try:
                this_url = STORY_BASE_URL % (id1, id2)
                get_html.set(url=this_url, header=HEADERS)
                try:
                    data = gzip.decompress(get_html.get(
                        method='GET')).decode("utf-8")
                except:
                    data = get_html.get(method='GET').decode("utf-8")

                share_count = get_share_count_re.findall(data)
                share_count = share_count[0] if len(share_count) > 0 else 0
                post_content = get_post_content_re.findall(data)
                post_content = post_content[0] if len(post_content) > 0 else 0

                post_text = get_post_content_text_re.findall(post_content)
                post_text = post_text[0] if len(post_text) > 0 else ''
                post_text = HTML_PARSER.unescape(post_text)
                post_text = GET_TEXT_RE.sub('', post_text).replace('\n', '')
                post_text = DELETE_SPACE_RE.sub(' ', post_text)
                post_time = get_post_time_re.findall(post_content)[0]

                fb_story = {
                    'page_id': id2,
                    'story_fbid': id1,
                    'post_time': post_time,
                    'share_count': share_count,
                    'post_html': post_content,
                    'post_text': post_text,
                    'comment': {
                        'count': 0,
                        'all_comments': []
                    }
                }

                # Get all comment
                have_more = True
                comment_data = data
                comment_sum = 0
                while have_more:
                    all_comment = get_comment_re.findall(comment_data)
                    for i in all_comment:
                        user_name = i[1]
                        user_name_2 = get_comment_user_2_re.findall(i[1])
                        if len(user_name_2) != 0:
                            user_name = user_name_2[0]

                        comment_html = i[2]
                        comment_text = HTML_PARSER.unescape(comment_html)
                        comment_text = GET_TEXT_RE.sub(
                            '', comment_text).replace('\n', '')
                        comment_text = DELETE_SPACE_RE.sub(' ', comment_text)

                        fb_story["comment"]["all_comments"].append({
                            'user_url': HTML_PARSER.unescape(i[0]),
                            'user_name': HTML_PARSER.unescape(user_name),
                            'comment_html': comment_html,
                            'comment_text': comment_text
                        })
                        comment_sum += 1

                    fb_story["comment"]["count"] = comment_sum
                    more_info = get_more_comment_url.findall(comment_data)
                    if len(more_info) != 0 and GET_ALL_COMMENTS:
                        this_url = "https://m.facebook.com" + \
                            HTML_PARSER.unescape(more_info[0])
                        get_html.set(url=this_url, header=HEADERS)

                        retry_count = 0
                        success = False
                        while (retry_count < MAX_RETRY) and (not success):
                            try:
                                comment_data = gzip.decompress(
                                    get_html.get(method='GET'))[9:]
                            except:
                                comment_data = get_html.get(method='GET')[9:]
                            try:
                                json_data = json.loads(comment_data)
                                success = True
                            except:
                                print(
                                    '    [COMMENT]Facebook has found there is some problem, wait sometime to retry...')
                                retry_count += 1
                                error_file_name = execution_time + '/errors/comment_' + \
                                    time.strftime("%Y%m%d-%H%M%S") + \
                                    '_' + id1 + '.html'
                                with open(error_file_name, 'w', encoding='utf-8') as file:
                                    file.write(comment_data.decode('utf-8'))
                                for _ in range(5):
                                    random_access_pages()
                                    time.sleep(5)
                                time.sleep(RETRY_SLEEP * retry_count)

                        comment_data = json_data['payload']['actions'][0]['html']
                        print(
                            '         This post has too many comments, we should stop for sometime to avoid facebook block account.')
                        time.sleep(PREVENT_BLOCK_SLEEP_TIME * random.random())
                        random_access_pages()
                    else:
                        have_more = False

                reaction_list_url_id = get_reaction_list_url_re.findall(data)[
                    0]
                reaction_url = REACTION_BASE_URL % (
                    reaction_list_url_id[0], reaction_list_url_id[1])
                fb_story['reaction'] = download_reaction(reaction_url, id1)
                post_success = True
            except:
                print(
                    '    [POST]Facebook has found there is some problem, wait sometime to retry...')
                post_retry_count += 1
                error_file_name = execution_time + '/errors/post_' + \
                    time.strftime("%Y%m%d-%H%M%S") + '_' + id1 + '.html'
                with open(error_file_name, 'w', encoding='utf-8') as file:
                    file.write(data)
                for _ in range(5):
                    random_access_pages()
                    time.sleep(5)
                time.sleep(RETRY_SLEEP * post_retry_count)

        with open(store_folder + "/fbid_%s.json" % id1, "w", encoding="utf-8") as f:
            f.write(json.dumps(fb_story))
            POST_GOT[id1] = True
            SUM_POSTS += 1
            if POSTS_TO_GET_EACH_PAGE != 0 and SUM_POSTS >= POSTS_TO_GET_EACH_PAGE:
                print('[INFO] got %d posts, go to next.' % SUM_POSTS)
                return


def download_reaction(url, fb_id):
    get_html = GetHtml()
    '''
    Reaction count:
        $1: reaction_type
        $2: count
    '''
    reaction_count_re = re.compile(
        r';reactionType&quot;:([0-9]+).*?<span aria-label="([0-9]*).*?(sx_.*?)"')
    reaction_type_dict = {
        '1': 'like',
        '2': 'love',
        '3': 'wow',
        '4': 'haha',
        '7': 'heartbreak',
        '8': 'angry',
    }
    '''
    One user reaction html
    '''
    reaction_html_re = re.compile(
        r'(<div class="_1uja.*?</div><i class="_59aq img sp_.*?</i></div>)')
    '''
    This user's info
        $1: This user's profile url
        $2: User name
    '''
    user_info_re = re.compile(
        r'<a class="darkTouch _1aj5 l" href="/(.*?)"><i class="img.*?" aria-label="(.*?)"')
    '''
    The class of reaction will be changed, we should use
    reactionType to build the dict only for this page.
    '''
    reaction_re = re.compile(
        r'<i class="_59aq img sp_.*? (.*?)"></i>')
    raction_dict = {}
    '''
    This url will load more users if reaction users is more than 50
    '''
    load_more_user_url_re = re.compile(
        r'href="(/ufi/reaction/profile/browser/fetch/\?.*?shown_ids=.*?)"')
    get_html.set(url=url, header=HEADERS)
    try:
        data = gzip.decompress(get_html.get(method='GET')).decode("utf-8")
    except:
        data = get_html.get(method='GET').decode("utf-8")

    reaction_count = reaction_count_re.findall(data)
    reaction_sum = 0
    res = {
        'count': {
            'sum': 0,
        },
        'users_detail': []
    }
    for i in reaction_count:
        reaction_sum += int(i[1])
        reaction_type = reaction_type_dict[i[0]] if reaction_type_dict.get(
            i[0]) else i[0]
        res['count'][reaction_type] = int(i[1])
        raction_dict[i[2]] = reaction_type

    res['count']['sum'] = reaction_sum
    print('             Getting detail user reactions for post id %s' % fb_id)
    have_more = True
    while have_more:
        reaction_html = reaction_html_re.findall(data)
        for i in reaction_html:
            user_info = user_info_re.findall(i)[0]
            reaction = reaction_re.findall(i)[0]
            reaction = raction_dict[reaction]
            res["users_detail"].append({
                'user_url': HTML_PARSER.unescape(user_info[0]),
                'user_name': HTML_PARSER.unescape(user_info[1]),
                'reaction': reaction
            })

        more_info = load_more_user_url_re.findall(data)
        if len(more_info) != 0 and GET_ALL_REACTIONS:
            this_url = "https://m.facebook.com" + \
                HTML_PARSER.unescape(more_info[0])
            get_html.set(url=this_url, header=HEADERS)

            retry_count = 0
            success = False
            while (retry_count < MAX_RETRY) and (not success):
                try:
                    data = gzip.decompress(get_html.get(method='GET'))[9:]
                except:
                    data = get_html.get(method='GET')[9:]
                try:
                    json_data = json.loads(data)
                    success = True
                except:
                    print(
                        '           [REACTION]Facebook has found there is some problem, wait sometime to retry...')
                    retry_count += 1
                    error_file_name = execution_time + '/errors/reaction_' + \
                        time.strftime("%Y%m%d-%H%M%S") + '_' + fb_id + '.html'
                    with open(error_file_name, 'w', encoding='utf-8') as file:
                        file.write(data.decode('utf-8'))
                    for _ in range(5):
                        random_access_pages()
                        time.sleep(5)
                    time.sleep(RETRY_SLEEP * retry_count)

            data = json_data['payload']['actions'][0]['html']
            try:
                more_data = json_data['payload']['actions'][1]['html']
                if more_data != "":
                    data += more_data
            except:
                continue
            print(
                '             This post has too many reactions, we should stop for sometime to avoid facebook block account.')
            time.sleep(PREVENT_BLOCK_SLEEP_TIME * random.random())
            random_access_pages()
        else:
            have_more = False
    return res


if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_with_save)
    download_pages()
    save_history()
    # ids = {
    #     '1673381129459180': '222778774519430',
    #     '2344197969167803': '222778774519430'
    # }
    # download_details(ids, '.')
