from functools import partial

import lxml.html as htmlparser
import regex

from ....config import TENSHI
from ...helpers import construct_site_based_regex, uwu

REGEX = construct_site_based_regex(TENSHI, extra_regex=r"/anime/([^?&/]+)")
TITLES_REGEX = regex.compile(r'<h1 class="mb-3">(.+?)</h1>')


def post_processor(session, stream_page):
    cookies = "__ddg1={}; __ddg2={}; __ddg2_={}".format(
        session.cookies.get("__ddg1_", ""),
        session.cookies.get("__ddg2", ""),
        session.cookies.get("__ddg2_", ""),
    )
    yield from (
        {
            "quality": int(_.group(2)),
            "stream_url": _.group(1),
            "headers": {"cookie": cookies},
        }
        for _ in regex.finditer(
            r'<source src="(.+?)" .+? size="([0-9]+)">', stream_page, flags=regex.S
        )
    )


def extract_urls(session, episode_page, *, post_processor):
    episode_page_content = session.get(episode_page)
    embed_page = (
        htmlparser.fromstring(episode_page_content.text).cssselect("iframe") or [{}]
    )[0].get("src")
    yield from post_processor(
        session, session.get(embed_page, headers={"referer": episode_page}).text
    )


def fetcher(
    session, url, check, match, *, post_processor=post_processor, domain=TENSHI
):
    uwu.bypass_ddos_guard(session, domain)
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
                lambda c: [*extract_urls(session, c, post_processor=post_processor)],
                "{}/{:d}".format(url, episode),
            ), episode


def metadata_fetcher(session, url, match, *, domain=TENSHI):

    uwu.bypass_ddos_guard(session, domain)
    url = match.group(0)

    return {"titles": TITLES_REGEX.findall(session.get(url).text)}
