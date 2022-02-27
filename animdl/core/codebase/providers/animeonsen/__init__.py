from functools import partial

import regex
import yarl

from ....config import ANIMEONSEN
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(ANIMEONSEN, extra_regex=r"/watch\?v=([^&?/]+)")

METADATA_REGEX = regex.compile(r'url: "(.+?)"')


def get_metadata(session, url):
    return session.get(url, headers={"origin": ANIMEONSEN.rstrip("/")}).json()


def stream_url_from_metadata(metadata):
    uri = metadata.get("player", {}).get("uri", {})
    return [
        {
            "stream_url": uri.get("stream"),
            "subtitle": [
                subtitle.get("location")
                for subtitle in uri.get("subtitles", {}).values()
            ],
            "headers": {
                "referer": ANIMEONSEN,
            },
        }
    ]


def fetcher(session, url, check, match):

    content_uri = yarl.URL(ANIMEONSEN + "watch")

    episode_page = session.get(
        content_uri.with_query({"v": match.group(1)}).human_repr()
    )
    metadata = get_metadata(session, METADATA_REGEX.search(episode_page.text).group(1))

    if check(1):
        yield partial(stream_url_from_metadata, metadata), 1

    for _ in range(2, int(metadata.get("metadata", {}).get("totalEpisodes", 2)) + 1):
        if check(_):
            yield partial(
                lambda episode: stream_url_from_metadata(
                    get_metadata(
                        session,
                        METADATA_REGEX.search(
                            session.get(
                                content_uri.with_query(
                                    {"v": match.group(1), "ep": episode}
                                ).human_repr()
                            ).text
                        ).group(1),
                    )
                ),
                _,
            ), _
