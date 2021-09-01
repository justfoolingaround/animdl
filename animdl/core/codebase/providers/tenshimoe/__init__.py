from functools import partial

import lxml.html as htmlparser

from ....config import TENSHI
from ...helper import construct_site_based_regex

TENSHI_ANIME_PAGE_REGEX = construct_site_based_regex(
    TENSHI, extra_regex=r'/anime/([^?&/]+)')


def extract_urls(session, episode_page):
    episode_page_content = session.get(episode_page)
    embed_page = (htmlparser.fromstring(episode_page_content.text).xpath(
        '//iframe') or [{}])[0].get('src')
    streams_page = session.get(embed_page, headers={'referer': episode_page})
    for content in htmlparser.fromstring(
                    streams_page.text).xpath('//source'):
                yield {'quality': int((content.get('title') or '0').strip('p')), 'stream_url': content.get('src')}


def fetcher(session, url, check):

    url = TENSHI_ANIME_PAGE_REGEX.search(url).group(0)

    episode_list_page = session.get(url)
    count = int(htmlparser.fromstring(episode_list_page.text).xpath(
                '//span[@class="badge badge-secondary align-top"]')[0].text_content())

    for episode in range(1, count + 1):
        if check(episode):
            yield partial(lambda c: [*extract_urls(session, c)], "{}/{:d}".format(url, episode)), episode
