import re

from ....config import ANIMEPAHE
from ...helper import construct_site_based_regex
from .inner import get_stream_url_from_kwik

from functools import partial, lru_cache

API_URL = ANIMEPAHE + "api"
SITE_URL = ANIMEPAHE

PLAYER_RE = construct_site_based_regex(
    ANIMEPAHE, extra_regex=r'/play/([^?&/]+)')
ID_RE = re.compile(r"/api\?m=release&id=([^&]+)")
KWIK_RE = re.compile(r"Plyr\|querySelector\|document\|([^\\']+)")


@lru_cache()
def get_session_page(session, page, release_id):
    return session.get(API_URL, params={'m': 'release', 'id': release_id, 'sort': 'episode_desc', 'page': page}).json()


def get_m3u8_from_kwik(session, kwik_url):
    """
    (Unused at the moment!)
    """
    kwik_page = session.get(kwik_url, headers={'referer': SITE_URL})
    match = KWIK_RE.search(kwik_page.text)
    if match:
        return "{10}://{9}-{8}.{7}.{6}.{5}/{4}/{3}/{2}/{1}.{0}".format(
            *match.group(1).split('|'))
    raise Exception(
        "Session fetch failure; please recheck and/or retry fetching anime URLs again. If this problem persists, please make an issue immediately.")


def get_stream_url(session, release_id, stream_session):

    stream_url_data = session.get(API_URL, params={
                                  'm': 'links', 'id': release_id, 'session': stream_session, 'p': 'kwik'})
    content = stream_url_data.json().get('data', [])

    for d in content:
        for quality, data in d.items():
            yield {'quality': quality, 'headers': {'referer': data.get('kwik')}, 'stream_url': get_m3u8_from_kwik(session, data.get('kwik'))}


def get_stream_urls_from_page(session, release_id, page, check):
    data = get_session_page(session, page, release_id).get('data')
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


def page_minimization(page_generator):
    return sorted(list(dict.fromkeys(page_generator)), reverse=True)


def bypass_ddos_guard(session):
    js_bypass_uri = re.search(
        r"'(.*?)'", session.get('https://check.ddos-guard.net/check.js').text).group(1)
    session.cookies.update(session.get(ANIMEPAHE + js_bypass_uri).cookies)


def fetcher(session, url, check):

    bypass_ddos_guard(session)

    match = PLAYER_RE.search(url)
    if match:
        url = "https://www.animepahe.com/anime/%s" % match.group(1)

    anime_page = session.get(url)
    release_id = ID_RE.search(anime_page.text).group(1)

    fpd = get_session_page(session, '1', release_id)

    if fpd.get('last_page') == 1:
        yield from get_stream_urls_from_page(session, release_id, '1', check)
        return

    for page in page_minimization(predict_pages(fpd.get('total'), check)):
        yield from get_stream_urls_from_page(session, release_id, page, check)
