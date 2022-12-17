from functools import partial

import lxml.html as htmlparser
import regex

from ....config import ZORO
from ...helpers import construct_site_based_regex

REGEX = construct_site_based_regex(ZORO, extra_regex=r"(/watch)?/[\w-]+-(\d+)")
TITLES_REGEX = regex.compile(r'<h2 class="film-name dynamic-name" .+?>(.+?)</h2>')

XHR_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": ZORO,
}


def int_or(string, *, default=0):
    if string.isdigit():
        return int(string)
    return default


SERVER_IDS = {4: "rapidvideo", 1: "rapidvideo", 5: "streamsb", 3: "streamtape"}


def extract_episode(session, data_id, title):
    for server in htmlparser.fromstring(
        session.get(
            ZORO + "ajax/v2/episode/servers",
            params={"episodeId": data_id},
            headers=XHR_HEADERS,
        )
        .json()
        .get("html")
    ).cssselect("div.server-item"):
        source_data = session.get(
            ZORO + "ajax/v2/episode/sources",
            params={"id": server.get("data-id")},
            headers=XHR_HEADERS,
        ).json()
        if source_data.get("type") != "iframe":
            yield {
                "stream_url": source_data.get("link"),
                "title": f"{server.get('data-type')} - {title}",
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
        session.get(ZORO + f"ajax/v2/episode/list/{slug}", headers=XHR_HEADERS)
        .json()
        .get("html")
    ).cssselect("a[title][data-number][data-id]"):
        episode_number = int_or(episode.get("data-number", "") or "")
        if check(episode_number):
            yield partial(
                lambda d_id, t: list(extract_episode(session, d_id, t)),
                d_id=episode.get("data-id"),
                t=episode.get("title"),
            ), episode_number


def metadata_fetcher(session, url, match):
    return {"titles": TITLES_REGEX.findall(session.get(ZORO + match.group(2)).text)}
