from collections import defaultdict
from functools import partial

import lxml.html as htmlparser
import regex
import yarl

REGEX = regex.compile(
    r"(?:https?://)?(?:\S+\.)?(?P<host>domdom\.stream|bestanime3\.xyz|kawaiifu\.com)/(?P<episode_page>anime/)?(?P<type>season/[^/]+|.+)/(?P<slug>[^?&#]+)"
)


def get_int(content):
    d = regex.search(r"[0-9]+", content)
    if d:
        return int(d.group(0))


def extract_stream_urls(session, urls):
    for url in urls:
        html_element = htmlparser.fromstring(session.get(url).text)
        for source in html_element.cssselect("source"):
            yield {
                "quality": get_int(source.get("data-quality")),
                "stream_url": source.get("src"),
                "headers": {"referer": url},
            }


def get_from_url(session, url):
    episodes = defaultdict(list)
    html_element = htmlparser.fromstring(session.get(url).text)

    for servers in html_element.cssselect(".list-server"):
        for element in servers.cssselect(".list-ep a"):
            episodes[get_int(element.text_content()) or 0].append(element.get("href"))
    return episodes


def fetcher(session, url, check, match):

    url = yarl.URL(url).with_host("bestanime3.xyz").human_repr()

    for episode, episode_urls in sorted(
        get_from_url(session, url).items(), key=lambda x: x[0]
    ):
        if check(episode):
            yield partial(
                lambda s, x: [*extract_stream_urls(s, x)], session, episode_urls
            ), episode
