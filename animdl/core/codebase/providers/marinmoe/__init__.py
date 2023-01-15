import functools

import lxml.html as htmlparser
import regex

from ....config import MARIN
from ...helpers import construct_site_based_regex, optopt

REGEX = construct_site_based_regex(MARIN, extra_regex=r"/anime/([^?&/]+)")

inertia_headers = {
    "x-inertia-version": "67023a9481a03976f4d5ae9b16e8f752",
    "x-inertia": "true",
}


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def iter_episode_streams(session, url):

    episodes_data = session.get(
        url,
        headers=inertia_headers,
    ).json()

    props = episodes_data.get("props", {})

    for episode in props.get("video", {}).get("data", {}).get("mirror", []):
        code = episode.get("code", {})

        yield {
            "stream_url": code.get("file"),
            "quality": code.get("width"),
            "title": " // ".join(
                _["text"]
                for _ in props.get("episode", {}).get("data", {}).get("title")[:2]
            ),
        }


@functools.lru_cache()
def fetch_anime_data(session, url):
    return HashableDict(
        session.get(
            url,
            headers=inertia_headers,
        ).json()
    )


def fetcher(session, url, check, match):
    url = match.group(0)

    anime_data = fetch_anime_data(session, url)

    count = int(anime_data.get("props", {}).get("anime", {}).get("last_episode", 0))

    for episode in range(1, count + 1):
        if check(episode):
            yield functools.partial(
                lambda url: list(iter_episode_streams(session, url)),
                f"{url}/{episode}",
            ), episode


def metadata_fetcher(session, url, match):

    url = match.group(0)

    anime_data = fetch_anime_data(session, url)

    return {
        "titles": [anime_data.get("props", {}).get("anime", {}).get("title")],
    }
