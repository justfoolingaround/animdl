import json
import regex
from base64 import b64decode, b64encode
from functools import partial

import lxml.html as htmlparser

ID_MATCHER = regex.compile(r"\?id=([^&]+)")
EMBED_URL_BASE = "https://animixplay.to/api/live"
EMBED_M3U8_MATCHER = regex.compile(r'player\.html[?#]([^#]+)')
EMBED_VIDEO_MATCHER = regex.compile(r'iframesrc="(.+?)"')

URL_ALIASES = {
    'bestanimescdn': 'omega.kawaiifucdn.xyz/anime3',
    'anicdn.stream': 'gogocdn.club',
    'ssload.info': 'gogocdn.club',
}

def fetching_chain(f1, f2, session, url, check=lambda *args: True):
    return f2(session, f1(session, url), check=check)

def from_site_url(session, url) -> dict:
    return json.loads(
        htmlparser.fromstring(
            session.get(url).content).cssselect('#epslistplace')[0].text)

def url_update(url):
    for key, item in URL_ALIASES.items():
        url = url.replace(key, item)
    return url

def extract_from_url(embed_url):
    on_url = EMBED_M3U8_MATCHER.search(embed_url)

    if not on_url:
        return []
    
    return [{'stream_url': url_update(b64decode(on_url.group(1)).decode())}]


def extract_from_embed(session, embed_url):
    embed_page = session.get(embed_url, allow_redirects=True)

    while embed_page.status_code not in [200, 403]:
        embed_page = session.get(embed_url, allow_redirects=True)

    if embed_page.status_code == 403:
        return []

    on_site = EMBED_VIDEO_MATCHER.search(embed_page.text)
    
    if on_site:
        return extract_from_url(on_site.group(1))

    return extract_from_url(str(embed_page.url))

def from_content_id(session, content_id):
    return session.post("https://api.gogocdn.club/v/{}".format(content_id), headers={'x-requested-with': 'XMLHttpRequest'}).json().get('m3u8')


def get_stream_url(session, data_url):
    content_id = ID_MATCHER.search(data_url)
    
    if content_id:
        return extract_from_embed(session, EMBED_URL_BASE + b64encode("{}LTXs3GrU8we9O{}".format(content_id.group(1), b64encode(content_id.group(1).encode()).decode()).encode()).decode()) or [{'stream_url': url_update(from_content_id(session, content_id.group(1)))}]

    return extract_from_url(data_url)

def gogoanime_parser(session, data: dict, *, check=lambda *args: True):
    for value in range(data.get('eptotal')):
        if check(value + 1):
            yield partial(lambda s, data_url: get_stream_url(s, data_url), session, data[str(value)]), value + 1
