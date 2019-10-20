# Download Facebook page, XU Zhengyi, 28/09/2019

import gzip
import json
import os
import random
import re
import time
from html.parser import HTMLParser
from urllib.parse import quote, unquote

from get_html import GetHtml

random.seed()
execution_time = time.strftime("%Y%m%d-%H%M%S")
if(os.path.isdir(execution_time) != True):
    os.makedirs(execution_time)

# List of id to collect
PAGE_IDS = [
    'PAGE_ID_YOU_WANT_TO_GET_1',
    'PAGE_ID_YOU_WANT_TO_GET_2',
]
COOKIES = 'YOUR_FACEBOOK_COOKIES'
NUM_TO_FETCH = 200
MAX_RETRY = 20
# Retry sleep in second
RETRY_SLEEP = 300
# Prevent block sleep time
PREVENT_BLOCK_SLEEP_TIME = 5


HEADERS = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': COOKIES,
    'dnt': '1',
    'origin': 'https://m.facebook.com',
    'referer': 'https://m.facebook.com/ConfederationGeneraleTravail/',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'x-requested-with': 'XMLHttpRequest',
    'x-response-format': 'JSONStream'
}
BASE_URL = "https://m.facebook.com/page_content_list_view/more/?page_id=%s&start_cursor=%s&num_to_fetch=%d&surface_type=posts_tab"
STORY_BASE_URL = "https://m.facebook.com/story.php?story_fbid=%s&id=%s"
REACTION_BASE_URL = "https://m.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier=%s&refid=%s"
START_CURSOR_BASE = {
    "timeline_cursor": None,
    "timeline_section_cursor": None,
    "has_next_page": True
}
HTML_PARSER = HTMLParser()
GET_TEXT_RE = re.compile(r'<[^>]*>')
DELETE_SPACE_RE = re.compile(r' {2,}')


def find_nex_start_cursor(json_require):
    for i in json_require:
        if i[0] == 'InitMMoreItemAutomatic':
            next_url = unquote(i[3][0]['href'])
            return json.loads(next_url.split('start_cursor=')[1].split('&')[0])
    return None


def download_pages():
    get_html = GetHtml()
    story_fbid = {}
    find_id_re = re.compile(r"story_fbid=([0-9]+)&amp;id=([0-9]+)")
    for page_id in PAGE_IDS:
        store_folder = execution_time + '/' + page_id
        os.mkdir(store_folder)
        start_cursor = START_CURSOR_BASE
        has_next_page = True
        nb_time = 0
        print('Getting page id: %s' % page_id)
        while has_next_page:
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
                        '     Facebook has found there is some problem, wait sometime to retry...')
                    retry_count += 1
                    time.sleep(RETRY_SLEEP)

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


def download_details(ids, store_folder):
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
        print('         Getting detail info for post id %s' % id1)
        this_url = STORY_BASE_URL % (id1, id2)
        get_html.set(url=this_url, header=HEADERS)
        try:
            data = gzip.decompress(get_html.get(method='GET')).decode("utf-8")
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
            if len(more_info) != 0:
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
                            '     Facebook has found there is some problem, wait sometime to retry...')
                        retry_count += 1
                        time.sleep(RETRY_SLEEP)

                comment_data = json_data['payload']['actions'][0]['html']
                print(
                    '         This post has too many comments, we should stop for sometime to avoid facebook block account.')
                time.sleep(PREVENT_BLOCK_SLEEP_TIME * random.random())
            else:
                have_more = False

        reaction_list_url_id = get_reaction_list_url_re.findall(data)[0]
        reaction_url = REACTION_BASE_URL % (
            reaction_list_url_id[0], reaction_list_url_id[1])
        fb_story['reaction'] = download_reaction(reaction_url, id1)

        with open(store_folder + "/fbid_%s.json" % id1, "w", encoding="utf-8") as f:
            f.write(json.dumps(fb_story))


def download_reaction(url, fb_id):
    get_html = GetHtml()
    '''
    Reaction count:
        $1: reaction_type
        $2: count
    '''
    reaction_count_re = re.compile(
        r';reactionType&quot;:([0-9]+).*?<span aria-label="([0-9]*)')
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
        r'(<div class="_1uja.*?</div><i class="_59aq img sp_ibiqbIoZ4BC.*?</i></div>)')
    '''
    This user's info
        $1: This user's profile url
        $2: User name
    '''
    user_info_re = re.compile(
        r'<a class="darkTouch _1aj5 l" href="/(.*?)"><i class="img.*?" aria-label="(.*?)"')
    '''
    sx_cb097b: like
    sx_890da8: love
    sx_84ce22: wow
    sx_45466b: haha
    sx_cca5fb: heartbreak
    sx_3376fe: angry
    '''
    reaction_re = re.compile(
        r'<i class="_59aq img sp_ibiqbIoZ4BC.*? (.*?)"></i>')
    raction_dict = {
        'sx_cb097b': 'like',
        'sx_07d5e9': 'like',
        'sx_890da8': 'love',
        'sx_34ffd8': 'love',
        'sx_84ce22': 'wow',
        'sx_02ad6e': 'wow',
        'sx_45466b': 'haha',
        'sx_01c980': 'haha',
        'sx_cca5fb': 'heartbreak',
        'sx_24d9b5': 'heartbreak',
        'sx_3376fe': 'angry',
        'sx_54ad47': 'angry'
    }
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
        res['count'][reaction_type_dict[i[0]]] = int(i[1])
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
        if len(more_info) != 0:
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
                        '     Facebook has found there is some problem, wait sometime to retry...')
                    retry_count += 1
                    time.sleep(RETRY_SLEEP)

            data = json_data['payload']['actions'][0]['html']
            try:
                more_data = json_data['payload']['actions'][1]['html']
                if more_data != "":
                    data += more_data
            except:
                continue
            print(
                '           This post has too many reactions, we should stop for sometime to avoid facebook block account.')
            time.sleep(PREVENT_BLOCK_SLEEP_TIME * random.random())
        else:
            have_more = False
    return res


if __name__ == '__main__':
    download_pages()
