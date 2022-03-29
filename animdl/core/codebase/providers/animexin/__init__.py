from base64 import b64decode
from functools import partial

import lxml.html as htmlparser
import regex

from ....config import ANIMEXIN
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(
    ANIMEXIN,
    extra_regex=r"/(?:anime/(?P<normal_slug>[^&?#/]+)|(?P<slug>.+?)-episode-\d+-.+?)",
)


TITLES_REGEX = regex.compile(r'<h2 itemprop="partOfSeries">(.+?)</h2>')
IFRAME_SRC = regex.compile(r'src="(.+?)"')

FURTHER_EXTRACTORS = {
    "gdriveplayer": "//gdriveplayer.to",
    "dailymotion": "https://www.dailymotion.com/",
}


def get_further_extractor_name(url):
    for extractor_name, prefix in FURTHER_EXTRACTORS.items():
        if isinstance(prefix, regex.Pattern) and prefix.search(url):
            return extractor_name
        if url.startswith(prefix):
            return extractor_name
    return None


def get_episode_metadata(episode_element):

    generic_episode_number = 0
    generic_episode_name = None

    e_n = episode_element.cssselect("div.epl-num")
    e_t = episode_element.cssselect("div.epl-title")

    if e_n:
        number = e_n[0].text_content()
        if number.isdigit():
            generic_episode_number = int(number)

    if e_t:
        generic_episode_name = (
            e_t[0].text_content()
            if not generic_episode_number
            else "Episode {} - {}".format(generic_episode_number, e_t[0].text_content())
        )

    return generic_episode_number, generic_episode_name


def extract(session, url, **opts):
    for options in htmlparser.fromstring(session.get(url).text).cssselect(
        "select.mirror > option[data-index][value]"
    ):
        embed_uri_match = IFRAME_SRC.search(b64decode(options.get("value")).decode())
        if not embed_uri_match:
            continue

        embed_uri = embed_uri_match.group(1)
        further_ext = get_further_extractor_name(embed_uri)

        if not further_ext or further_ext in ["gdriveplayer"]:
            continue

        yield {"stream_url": embed_uri, "further_extraction": (further_ext, {}), **opts}


def fetcher(session, url, check, match):

    if match.group("slug"):
        url = ANIMEXIN + "anime/{}".format(match.group("slug"))

    for episode in htmlparser.fromstring(session.get(url).text).cssselect(
        ".eplister li[data-index] > a"
    )[::-1]:
        number, name = get_episode_metadata(episode)

        if check(number):
            yield partial(
                lambda s, u, **kwargs: list(extract(s, u, **kwargs)),
                session,
                episode.get("href"),
                title=name,
            ), number


def metadata_fetcher(session, url, match):

    if match.group("slug"):
        url = ANIMEXIN + "anime/{}".format(match.group("slug"))

    return {"titles": TITLES_REGEX.findall(session.get(url).text)}
