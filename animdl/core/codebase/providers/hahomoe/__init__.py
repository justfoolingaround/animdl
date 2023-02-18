import functools

import lxml.html as htmlparser

from ....config import HAHO
from ...helpers import construct_site_based_regex, optopt

REGEX = construct_site_based_regex(HAHO, extra_regex=r"/anime/([^?&/]+)")

TITLES_REGEX = optopt.regexlib.compile(r'<h1 class="mb-3">(.+?)</h1>')
SORUCES_REGEX = optopt.regexlib.compile(
    r'<source.*? src="(.+?)" title="([0-9]+?)p" .+?>',
    flags=optopt.regexlib.I,
)


def iter_stream_urls(session, episode_page):
    episode_page_content = session.get(episode_page)

    iframes = htmlparser.fromstring(episode_page_content.text).cssselect("iframe")

    if not iframes:
        return

    embed_source = session.get(
        iframes[0].get("src"), headers={"referer": episode_page}
    ).text

    for source in SORUCES_REGEX.finditer(embed_source):
        yield {
            "stream_url": source.group(1),
            "quality": int(source.group(2)),
        }


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
            yield functools.partial(
                (lambda url: list(iter_stream_urls(session, url))), f"{url}/{episode}"
            ), episode


def metadata_fetcher(session, url, match):

    url = match.group(0)

    return {"titles": TITLES_REGEX.findall(session.get(url).text)}
