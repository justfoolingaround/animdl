import base64
from collections import defaultdict
from functools import lru_cache, partial

import yarl

from ....config import CRUNCHYROLL, SUPERANIME_CRUNCHYROLL
from ... import helpers
from .api import Kamyroll

VRV_RESPONSE_REGEX = helpers.optopt.regexlib.compile(
    r"^#EXT-X-STREAM-INF:.*?RESOLUTION=\d+x(?P<resolution>\d+).*?\n(.+?)$",
    flags=helpers.optopt.regexlib.MULTILINE,
)
CR_GUID_REGEX = helpers.optopt.regexlib.compile(
    r"crunchyroll\.com(?:/.+?)?/series/(.+?)(?:/|$)"
)


REGEX = helpers.optopt.regexlib.compile(
    r"kamyroll://(?:.+?\.)+?crunchyroll\.com(?:/.+?)?/series/(.+?)(?:/|$)"
)


def fix_subtitle_url(url):
    parsed_url = yarl.URL(url)

    token = parsed_url.query.get("token")

    if token is None:
        return url

    url_base = base64.urlsafe_b64decode(token + "=" * (4 - len(token) % 4)).decode()

    return url_base[2:-2]


def fetch_streams(api: Kamyroll, medias: "list"):

    superanime_subtitle = SUPERANIME_CRUNCHYROLL.get("subtitle_language") or ""

    for stream_attrs, media_id in medias:
        streams_data = api.fetch_streams(media_id)

        if not streams_data["streams"]:
            continue

        selected_streams = [
            _
            for _ in streams_data["streams"]
            if _["hardsub_locale"] == superanime_subtitle
        ] or streams_data["streams"]
        subtitles = streams_data["subtitles"]

        for stream in selected_streams:
            yield {
                "stream_url": stream["url"],
                "subtitle": [fix_subtitle_url(_["url"]) for _ in subtitles],
                **stream_attrs,
            }


@lru_cache()
def fetch_episodes(api: Kamyroll, media_id):
    seasons = api.fetch_seasons(media_id)["items"]
    episodes = defaultdict(list)

    for season in seasons:
        for episode in season["episodes"]:
            episode_number = episode["episode_number"] or 0
            episodes[episode_number].append(
                (
                    {
                        "title": f'{episode["title"]} ({season["title"]})',
                    },
                    episode["id"],
                )
            )
    return episodes


def fetcher(session, url, check, match):
    api = Kamyroll(session)
    cr_guid = match.group(1)

    episodes = fetch_episodes(api, cr_guid)

    sorted_episodes = sorted(episodes.items(), key=lambda x: x[0])

    for episode_number, medias in sorted_episodes:
        if check(episode_number):
            yield partial(
                lambda medias: list(fetch_streams(api, medias)),
                medias,
            ), episode_number


def metadata_fetcher(session, url, match):
    api = Kamyroll(session)
    cr_guid = match.group(1)

    metadata = api.fetch_media(cr_guid)

    return {
        "title": [metadata["title"]],
    }
