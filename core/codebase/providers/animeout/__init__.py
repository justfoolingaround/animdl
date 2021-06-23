from functools import partial
from urllib.parse import unquote

import lxml.html as htmlparser

from .inner.indexer import index_by_url


def group_episodes(contents):
    grouped = {}
    for r in contents:
        grouped.setdefault(r.get('episode', 0) or 0, [])
        grouped.get(r.get('episode', 0) or 0, []).append(r)
    return grouped
    
    
def fetcher(session, url, check):
    with session.get(url) as animeout_page:
        parsed = htmlparser.fromstring(animeout_page.text)
            
    for episode, content in sorted(group_episodes([index_by_url(unquote(_.get('href'))) for _ in parsed.xpath('//article//a') if "Download" in _.text_content()]).items()):
        if check(episode):
            yield partial(lambda x: x, [{'quality': _.get('quality') or 'unknown', 'stream_url': 'https://public.animeout.xyz/' + _.get('url', '').removeprefix('https://').removeprefix('http://')} for _ in content]), episode