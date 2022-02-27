"""
THANKS FOR ADDING STREAMSB AND STREAMTAPE DUMMIES
"""

from functools import partial
from ...helper import construct_site_based_regex
from ....config import ZORO

import lxml.html as htmlparser

REGEX = construct_site_based_regex(ZORO, extra_regex=r"(/watch)?/[\w-]+-(\d+)")


def int_or(string, *, default=0):
    if string.isdigit():
        return int(string)
    return default


SERVER_IDS = {4: "rapidvideo", 1: "rapidvideo", 5: "streamsb", 3: "streamtape"}


def extract_episode(session, data_id, title):
    for server in htmlparser.fromstring(
        session.get(
            "https://zoro.to/ajax/v2/episode/servers", params={"episodeId": data_id}
        )
        .json()
        .get("html")
    ).cssselect("div.server-item"):
        source_data = session.get(
            "https://zoro.to/ajax/v2/episode/sources",
            params={"id": server.get("data-id")},
        ).json()
        if source_data.get("type") != "iframe":
            yield {
                "stream_url": source_data.get("link"),
                "title": "{} - {}".format(server.get("data-type"), title),
            }
            continue

        cdn = SERVER_IDS.get(source_data.get("server"), "unavailable")

        if cdn in ["streamsb", "streamtape", "unavailable"]:
            continue

        yield {
            "stream_url": source_data.get("link"),
            "further_extraction": (
                cdn,
                {"headers": {"Referer": ZORO}},
            ),
            "title": "{} - {}".format(server.get("data-type", "").upper(), title),
        }


def fetcher(session, url, check, match):
    slug = match.group(2)

    for episode in htmlparser.fromstring(
        session.get(ZORO + "/ajax/v2/episode/list/{}".format(slug)).json().get("html")
    ).cssselect("a[title][data-number][data-id]"):
        episode_number = int_or(episode.get("data-number", "") or "")
        if check(episode_number):
            yield partial(
                lambda d_id, t: list(extract_episode(session, d_id, t)),
                d_id=episode.get("data-id"),
                t=episode.get("title"),
            ), episode_number
