"""
This provider is hard-coded to give out the maximum qualtiy possible.

This is, in fact, due to code limitation of animdl to handle it on site-access.
"""

import re
from base64 import b64decode
from collections import defaultdict
from functools import partial

import lxml.html as htmlparser

from ....config import ANIMEKAIZOKU
from ...helper import construct_site_based_regex, uwu
from .indexer import name_index

REGEX = construct_site_based_regex(ANIMEKAIZOKU, extra_regex=r'/([^?&/]+)')


ON_NEW_TAB = re.compile(r'openInNewTab\("([^"]+?)"\)')
ANIMEKAIZOKU_DDL = re.compile(r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)')
DDL_DIVID = re.compile(r'glist-(\d+)')
DDL_POSTID = re.compile(r'"postId":"(\d+)"')

def get_indexed(elements):
    for element in elements:
        yield name_index(element)

def group_episodes(iterab):
    episode_dict = defaultdict(lambda: list())
    for content in sorted(iterab, key=lambda x: x.get('episode', 0)):
        episode_dict[content.get('episode') or 0].append(content)
    return episode_dict


def admin_ajax(session, data):
    return session.post(ANIMEKAIZOKU + "wp-admin/admin-ajax.php", headers={'x-requested-with': 'XMLHttpRequest'}, data=data)

def get_links(session, quality, element_dicts, post_id, div_id):
    def fast_yield():
        for element_dict in element_dicts:
            num = re.search(r"'([^']+?)'", element_dict.get('element', {}).get('onclick')).group(1)
            link = b64decode(ON_NEW_TAB.search(admin_ajax(session, {'action': 'DDL', 'post_id': post_id, 'div_id': div_id, 'tab_id': 2, 'num': num, 'folder': 0}).text).group(1)).decode('utf-8')
            stream_url = uwu.bypass(link)
            yield {'quality': quality, 'stream_url': session.get(stream_url, headers={'referer': link}, allow_redirects=False).headers.get('location'), 'headers': {'referer': stream_url}}
    return [*fast_yield()]

def fetcher(session, url, check):

    response = session.get(url).text

    div_id = DDL_DIVID.search(response).group(1)
    post_id = DDL_POSTID.search(response).group(1)
    
    content = htmlparser.fromstring(admin_ajax(session, {'action': 'DDL', 'post_id': post_id, 'div_id': div_id, 'tab_id': 2, 'folder': True}).text)
    selected = sorted(get_indexed(content.cssselect('.downloadbutton')), key=lambda x: x.get('quality', 0), reverse=True)[0]
    
    num = re.search(r"'([^']+?)'", selected.get('element', {}).get('onclick')).group(1)

    episodes = htmlparser.fromstring(admin_ajax(session, {'action': 'DDL', 'post_id': post_id, 'div_id': div_id, 'tab_id': 2, 'num': num, 'folder': 1}).text)

    for episode, streams in group_episodes(get_indexed(episodes.cssselect('.downloadbutton'))).items():
        if check(episode):
            yield partial(get_links, session, selected.get('quality'), streams, post_id, div_id), episode
