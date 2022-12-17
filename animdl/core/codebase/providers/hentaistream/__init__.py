from functools import partial

import lxml.html as htmlparser
import regex

from ....config import HENTAISTREAM
from ...helpers import construct_site_based_regex

EPISODE_REGEX = regex.compile(r"/\d+/[^&?/]+")
TITLES_REGEX = regex.compile(r'<h1 class="entry-title" itemprop="name">(.+?)</h1>')


REGEX = construct_site_based_regex(
    HENTAISTREAM, extra_regex=r"/hentai/([^?&/]+)(?:/\d+)?"
)

EXTRACTOR_REGEX = regex.compile(r"src: '(.+?)',\s+type: '.+?',\s+size: (\d+),")
SUBTITLE_URL_REGEX = regex.compile(r"subUrl: '(.+?)'")


def fetch_streams(session, episode_url, **opts):

    episode_page = session.get(HENTAISTREAM + episode_url[1:]).text
    subtitles = SUBTITLE_URL_REGEX.findall(episode_page)

    for url, size in EXTRACTOR_REGEX.findall(episode_page):

        yield {
            "stream_url": url,
            "quality": int(size),
            "headers": {"referer": HENTAISTREAM},
            "subtitle": subtitles,
        }


def fetcher(session, url, check, match):

    episodes_page = htmlparser.fromstring(
        session.get(HENTAISTREAM + f"hentai/" + match.group(1)).text
    )

    for urls in episodes_page.cssselect("div.eplister a"):
        number, title, date = map(
            htmlparser.HtmlElement.text_content, urls.cssselect('div[class^="epl"]')
        )

        episode_number = int(number) if number.isdigit() else 0

        if check(episode_number):
            yield partial(
                lambda url, **opts: list(fetch_streams(session, url, **opts)),
                urls.get("href"),
                title=f"{title} ({date})",
            ), episode_number


def metadata_fetcher(session, url, match):

    episode_url = HENTAISTREAM + f"hentai/" + match.group(1)

    return {"titles": TITLES_REGEX.findall(session.get(episode_url).text)}
