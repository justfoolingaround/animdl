import re
from functools import partial

import lxml.html as htmlparser

from ....config import ANIMTIME
from ...helper import construct_site_based_regex

CONTENT_RE = re.compile(r't\[t\.([^=]+)=(\d+)\]')
CONTENT_SLUG_RE = construct_site_based_regex(
    ANIMTIME, extra_regex=r'/title/([^/?&]+)')


def get_first_item(iterables, check):
    for item in iterables:
        if check(item):
            return item


def get_content(url, js_content):
    content_slug = CONTENT_SLUG_RE.match(url).group(1)
    for match in CONTENT_RE.finditer(js_content):
        if match.group(2) == content_slug:
            return match


def fetcher(session, url, check):
    with session.get(url) as animtime_page:
        scripts = htmlparser.fromstring(animtime_page.text).xpath('//script')

    main = get_first_item(scripts, lambda e: e.get(
        'src', '').startswith('main')).get('src')

    with session.get(ANIMTIME + main) as mainjs:
        content = mainjs.text

    content = content[content.index('tm=function(t)'):]

    anime = get_content(url, content)
    episodes = int(re.search(
        r'zd.*?\[tm\.{}\]=(\d+)'.format(re.escape(anime.group(1))), content).group(1))
    constructor, end = re.search(
        '\[tm\.{}\]=function\(t\){{return"([^"]+)\"\+t\+\"([^"]+)'.format(re.escape(anime.group(1))), content).groups()
    for episode in range(1, episodes + 1):
        if check(episode):
            yield partial(lambda x: [{'stream_url': x, 'referer': ANIMTIME}], constructor + "{:03d}".format(episode) + end), episode
