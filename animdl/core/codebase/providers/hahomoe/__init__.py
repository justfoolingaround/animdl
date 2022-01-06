from functools import partial

import lxml.html as htmlparser

from ....config import HAHO
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(HAHO, extra_regex=r"/anime/([^?&/]+)")


def extract_urls(session, episode_page):
    episode_page_content = session.get(episode_page)
    embed_page = (
        htmlparser.fromstring(episode_page_content.text).cssselect("iframe") or [{}]
    )[0].get("src")
    streams_page = session.get(embed_page, headers={"referer": episode_page})

    def _get_quality(quality_string):
        q = quality_string.rstrip("pP")
        if q.isdigit():
            return int(q)
        return None

    yield from (
        {"stream_url": _.get("src"), "quality": _get_quality(_.get("title"))}
        for _ in htmlparser.fromstring(streams_page.text).cssselect("source")
    )


def fetcher(session, url, check, match):
    url = match.group(0)

    episode_list_page = session.get(url)
    count = int(
        htmlparser.fromstring(episode_list_page.text)
        .cssselect("span.badge")[0]
        .text_content()
    )

    for episode in range(1, count + 1):
        if check(episode):
            yield partial(
                lambda c: list(extract_urls(session, c)), "{}/{:d}".format(url, episode)
            ), episode
