import re

import lxml.html as htmlparser

from ...config import ANIME1
from ...helper import construct_site_based_regex

from functools import partial

from requests.exceptions import Timeout

EPISODE_RE = construct_site_based_regex(ANIME1, extra_regex=r'/watch/([^?&/]+)/episode-\d+')
STREAM_EXTRACTOR_RE = re.compile(r'(?<=file: ")(?:(?!\").)+')

is_healthy = lambda session, url: session.get(url, stream=True, verify=False, timeout=3).ok

def extract(session, url):
    with session.post(ANIME1 + "content/episode/", verify=False, headers={'referer': url, 'x-requested-with': 'XMLHttpRequest'}) as content_access:
        cooked_cookie = content_access.headers.get('set-cookie', '')
    
    healthy = False

    while not healthy:        
        with session.get(url, verify=False, headers={'cookie': cooked_cookie}) as episode:
            stream_url = STREAM_EXTRACTOR_RE.search(episode.text).group(0)
        cooked_cookie = episode.headers.get('set-cookie', '')
        healthy = is_healthy(session, stream_url)
        
    return {'quality': 'unknown', 'stream_url': stream_url}


def fetcher(session, url, check):
    match = EPISODE_RE.search(url)
    if match:
        url = ANIME1 + "watch/{}".format(match.group(1))
        
    with session.get(url, verify=False) as episodes_page:
        parsed = htmlparser.fromstring(episodes_page.text)
    
    for episode in parsed.xpath('//div[@class="left-left"]/ul/li/a'):
        x = re.search(r"Episode (\d+)", episode.text_content())
        c = int(x.group(1) if x else 0)
        if check(c):
            yield partial(extract, session, episode.get('href')), c