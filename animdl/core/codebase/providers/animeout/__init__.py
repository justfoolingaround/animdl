from collections import defaultdict
from functools import partial
from urllib.parse import unquote

import lxml.html as htmlparser

from ....config import ANIMEOUT
from ...helper import construct_site_based_regex
from .inner.indexer import index_by_url

REGEX = construct_site_based_regex(ANIMEOUT, extra_regex=r'/([^?&/]+)')

def group_episodes(contents):
    grouped = defaultdict(list)
    for r in contents:
        grouped[r.get('episode') or 0].append(r)
    return grouped


def fetcher(session, url, check):
    animeout_page = session.get(url)
    parsed = htmlparser.fromstring(animeout_page.text)

    for episode, content in sorted(group_episodes([index_by_url(unquote(_.get(
            'href'))) for _ in parsed.cssselect('.article-content a[href$="mkv"]') if "Download" in _.text_content()]).items()):
        if check(episode):
            yield partial(lambda x: x, [{'quality': _.get('quality') or 'unknown', 'stream_url': 'https://public.animeout.xyz/' + _.get('url', '').removeprefix('https://').removeprefix('http://')} for _ in content]), episode
