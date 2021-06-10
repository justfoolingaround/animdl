import re

import requests

from ...config import ANIMEPAHE
from ...helper import construct_site_based_regex

from functools import partial

API_URL = ANIMEPAHE + "api"
SITE_URL = ANIMEPAHE

PLAYER_RE = construct_site_based_regex(ANIMEPAHE, extra_regex=r'/play/([^?&/]+)')
ID_RE = re.compile(r"/api\?m=release&id=([^&]+)")
KWIK_RE = re.compile(r"Plyr\|querySelector\|document\|([^\\']+)")

def get_session_page(session, page, release_id):
    with session.get(API_URL, params={'m': 'release', 'id': release_id, 'sort': 'episode_desc', 'page': page}) as response:
        return response.json()

def get_m3u8_from_kwik(session, kwik_url):
    """
    Better than 99% of those 'kwik_extractor.py' in **most** tools that download from AnimePahe.
    """
    with session.get(kwik_url, headers={'referer': SITE_URL}) as kwik_page:
        match = KWIK_RE.search(kwik_page.text)
        if match:
            return "{10}://{9}-{8}-{7}.{6}.{5}/{4}/{3}/{2}/{1}.{0}".format(*match.group(1).split('|'))
        raise Exception("Session fetch failure; please recheck and/or retry fetching anime URLs again. If this problem persists, please make an issue immediately.")
        
def get_stream_url(session, release_id, stream_session):
    
    with session.get(API_URL, params={'m': 'links', 'id': release_id, 'session': stream_session, 'p': 'kwik'}) as stream_url_data:
        content = stream_url_data.json().get('data', [])
        
    for d in content:
        for quality, data in d.items():
            yield {'quality': quality, 'headers': {'referer': data.get('kwik')}, 'stream_url': get_m3u8_from_kwik(session, data.get('kwik'))}
    

def get_stream_urls_from_data(session, release_id, data, check):
    for content in reversed(data):
        if check(content.get('episode', 0)):
            yield partial(lambda session, release_id, content: ([*get_stream_url(session, release_id, content.get('session'))]), session, release_id, content), content.get('episode', 0)

def predict_pages(total, check):
    """
    A calculative function to minimize API calls.
    """
    for x in range(1, total + 1):
        if check(x):
            yield (total - x) // 30 + 1
        

def fetcher(session: requests.Session, url, check):
    
    match = PLAYER_RE.search(url)
    if match:
        url = "https://www.animepahe.com/anime/%s" % match.group(1)
    
    with session.get(url) as anime_page:
        release_id = ID_RE.search(anime_page.text).group(1)
    
    fpd = get_session_page(session, '1', release_id)

    if fpd.get('last_page') == 1:
        yield from get_stream_urls_from_data(session, release_id, fpd.get('data'), check)
        return

    for pages in predict_pages(fpd.get('total'), check):
        yield from get_stream_urls_from_data(session, release_id, get_session_page(session, str(pages), release_id).get('data'), check)