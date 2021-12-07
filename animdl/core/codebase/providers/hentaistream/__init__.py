import base64
from functools import partial

import lxml.html as htmlparser
import regex

from ....config import HENTAISTREAM
from ...helper import construct_site_based_regex

EPISODE_REGEX = regex.compile(r"/\d+/[^&?/]+")

REGEX = construct_site_based_regex(
    HENTAISTREAM, extra_regex=r'/(anime|\d+)/([^?&/]+)')

def bypass_ddos_guard(session, base_uri='https://hentaistream.moe/'):
    js_bypass_uri = regex.search(
        r"'(.*?)'",
        session.get('https://check.ddos-guard.net/check.js').text).group(1)
    
    session.get(base_uri + js_bypass_uri)

def get_episodes_page(session, url):
    bypass_ddos_guard(session)
    return htmlparser.fromstring(session.get(url).text).cssselect('li[itemscope] > a[href^="https://hentaistream.moe/anime/"]')[0].get('href')


def extract_from_site(session, episode_url, **opts):

    for embed in htmlparser.fromstring(session.get(episode_url).text).cssselect('iframe'):
        _, content_uri = embed.get('src', '#').split('#')
        base, *_sub = base64.b64decode(content_uri).decode()[4:].split(';')

        subtitle = list(base + _ + ".vtt" for _ in _sub)

        yield from ({**_, **opts, **({'subtitle': subtitle} if subtitle else {})} for _ in
            ({
                'quality': 720,
                'stream_url': base + "x264.720p.mp4",
            },
            {
                'quality': 1080,
                'stream_url': base + "av1.1080p.webm",
            },
            {
                'quality': 2160,
                'stream_url': base + "av1.2160p.webm",
            })
        )

def fetcher(session, url, check):
    
    if EPISODE_REGEX.search(url):
        url = get_episodes_page(session, url)
    
    for episode_page in htmlparser.fromstring(session.get(url).text).cssselect('li[data-index] > a')[::-1]:
        number, title, date = (_.text_content() for _ in episode_page.cssselect('div[class^="epl"]'))
        episode_number = int(number) if number.isdigit() else 0
        
        if check(episode_number):
            yield partial(lambda ep, **opts: list(extract_from_site(session, ep, **opts)), episode_page.get('href'), title="{} ({})".format(title, date)), episode_number
