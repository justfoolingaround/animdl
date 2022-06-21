from collections import defaultdict
from functools import partial

import regex

from ....config import CRUNCHYROLL, KAMYROLL_API
from ..crunchyroll import metadata_fetcher
from .api import get_media_streams

REGEX = regex.compile(r"kamyroll://(?:.+?\.)+?crunchyroll\.com/([^&?/]+)")

MEDIA_ID_REGEX = regex.compile(r'\{"isAuthenticated":.+?"mediaId":"(.+?)".+?\}')

CRUNCHYROLL_EPISODES_REGEX = regex.compile(
    r"<crunchyroll:mediaId>(\d+)</crunchyroll:mediaId>"
    r".+?<crunchyroll:episodeTitle>(.+?)</crunchyroll:episodeTitle>"
    r".+?<crunchyroll:episodeNumber>(\d+)</crunchyroll:episodeNumber>",
    flags=regex.DOTALL,
)


def extract_streams(session, medias: "list"):

    collected_streams = []
    collected_subtitles = []

    for (media_id, title) in medias:
        streams = get_media_streams(session, KAMYROLL_API, media_id)

        collected_subtitles.extend(
            _["url"] for _ in streams.get("subtitles", []) if _["locale"] == "en-US"
        )

        for stream in streams.get("streams", []):
            if stream["url"] not in streams and not stream["hardsub_locale"]:
                collected_streams.append(
                    {
                        "stream_url": stream["url"],
                        "title": title,
                        **(
                            {"subtitle": collected_subtitles}
                            if collected_subtitles
                            else {}
                        ),
                    }
                )

    return collected_streams


def get_media_from_rss(session, rss_url):

    episodes = defaultdict(list)

    for match in list(CRUNCHYROLL_EPISODES_REGEX.finditer(session.get(rss_url).text))[
        ::-1
    ]:
        episodes[int(match.group(3))].append(match.group(1, 2))

    return episodes


def fetcher(session, url, check, match):
    rss_url = CRUNCHYROLL + match.group(1) + ".rss"

    for episode, medias in get_media_from_rss(
        session,
        rss_url,
    ).items():
        if check(int(episode)):
            yield partial(extract_streams, session, medias), episode
