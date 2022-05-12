from functools import partial

import regex

from ....config import CRUNCHYROLL, KAMYROLL_API
from ..crunchyroll import metadata_fetcher
from .api import fetch_seasons, get_media_streams

REGEX = regex.compile(r"kamyroll://(?:.+?\.)+?crunchyroll\.com/([^&?/]+)")

MEDIA_ID_REGEX = regex.compile(r'\{"isAuthenticated":.+?"mediaId":"(.+?)".+?\}')


def fetch_v2_media_id(session, url):
    return MEDIA_ID_REGEX.search(session.get(url).text).group(1)


def extract_streams(session, medias: "list"):

    collected_streams = []
    collected_subtitles = []

    for media in medias:
        streams = get_media_streams(session, KAMYROLL_API, media["id"])

        collected_subtitles.extend(
            _["url"] for _ in streams.get("subtitles", []) if _["locale"] == "en-US"
        )

        for stream in streams.get("streams", []):
            if stream["url"] not in streams and not stream["hardsub_locale"]:
                collected_streams.append(
                    {
                        "stream_url": stream["url"],
                        "title": media["title"],
                        **(
                            {"subtitle": collected_subtitles}
                            if collected_subtitles
                            else {}
                        ),
                    }
                )

    return collected_streams


def fetcher(session, url, check, match):
    media_id = fetch_v2_media_id(session, CRUNCHYROLL + match.group(1))

    for episode, media in fetch_seasons(
        session,
        KAMYROLL_API,
        media_id,
        predicate=lambda episode: check(episode["episode_number"]),
    ).items():
        yield partial(extract_streams, session, media), episode
