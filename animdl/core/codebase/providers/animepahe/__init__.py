import functools

import regex

from animdl.utils import optopt

from ....config import ANIMEPAHE
from ...helpers import construct_site_based_regex
from .inner import get_animepahe_url

REGEX = construct_site_based_regex(ANIMEPAHE, extra_regex=r"/(anime|play)/([^?&/]+)")

ID_RE = optopt.regexlib.compile(r'let id = "(.+?)"')
KWIK_RE = optopt.regexlib.compile(r"Plyr\|(.+?)'")

STREAMS_REGEX = optopt.regexlib.compile(
    r'<a href="(?P<url>.+?)" .+? class="dropdown-item">.+? (?P<resolution>\d+)p.+?</a>'
)

TITLES_REGEX = optopt.regexlib.compile(r"<h1>(.+?)</h1>")


def get_streams_from_embed_url(session, embed_uri):
    embed_page = session.get(embed_uri, headers={"referer": ANIMEPAHE}).text
    return "{}://{}-{}.{}.{}.{}/{}/{}/{}/{}.{}".format(
        *KWIK_RE.search(embed_page).group(1).split("|")[::-1]
    )


def iter_stream_url_from_stream_session(session, release_id, stream_session):
    stream_url_data = session.get(
        ANIMEPAHE + f"play/{release_id}/{stream_session}",
    )

    for url, resolution in STREAMS_REGEX.findall(stream_url_data.text):
        yield {
            "quality": int(resolution),
            "stream_url": get_animepahe_url(session, url),
        }


def iter_episode_streams(session, release_id, per_page, episode_number):

    current_page = episode_number // per_page + 1

    episode = fetch_session(session, release_id, page=current_page)["data"][
        episode_number % per_page - 1
    ]

    yield from iter_stream_url_from_stream_session(
        session, release_id, episode["session"]
    )


@functools.lru_cache()
def fetch_session(session, release_id, *, page=None):
    return session.get(
        ANIMEPAHE + "api",
        params={"m": "release", "id": release_id, "sort": "episode_asc", "page": page},
    ).json()


def fetcher(session, url, check, match):

    if match.group(1) == "play":
        url = ANIMEPAHE + f"anime/{match.group(2)}"

    anime_page = session.get(url)

    release_id = ID_RE.search(anime_page.text).group(1)

    initial_session = fetch_session(session, release_id, page=1)
    per_page = initial_session["per_page"]
    total = initial_session["total"]

    for episode_number in range(1, total + 1):
        if check(episode_number):
            yield functools.partial(
                (
                    lambda episode_number: iter_episode_streams(
                        session, release_id, per_page, episode_number
                    )
                ),
                episode_number,
            ), episode_number


def metadata_fetcher(session, url, match):
    if match.group(1) == "play":
        url = ANIMEPAHE + f"anime/{match.group(2)}"

    return {
        "titles": TITLES_REGEX.findall(session.get(url).text),
    }
