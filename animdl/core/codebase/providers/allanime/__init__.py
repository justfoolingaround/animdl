from collections import defaultdict
from functools import partial

import yarl

from ....config import ALLANIME, SUPERANIME_RETURN_ALL, SUPERANIME_TYPE_OF
from ...helpers import construct_site_based_regex, optopt, superscrapers
from .gql_api import api

REGEX = construct_site_based_regex(ALLANIME, extra_regex=r"/(?:anime|watch)/([^?&/]+)")

LEGACY_CONTENT_REGEX = optopt.regexlib.compile(
    r'date:g,data:"({.+?})"}},calling:', optopt.regexlib.DOTALL
)


def iter_episodes(
    episode_dictionary: dict,
    *,
    selected_type_of: str = SUPERANIME_TYPE_OF,
):
    episodes = defaultdict(list)

    for type_of, episode_numbers in episode_dictionary.items():
        if type_of != selected_type_of:
            continue

        for episode in episode_numbers:
            episodes[int(episode) if episode.isdigit() else 0].append(
                (type_of, episode)
            )

    yield from sorted(episodes.items(), key=lambda x: x[0])


def to_clock_json(url: str):
    return optopt.regexlib.sub(r"(?<=/clock)(?=[?&#])", ".json", url, count=1)


def fetch_legacy(session, episode, type_of, show_id):
    """
    This is a fallback method for fetching the content of an episode
    when the GQL hits server-side rate-limits.
    """

    match = LEGACY_CONTENT_REGEX.search(
        session.get(
            ALLANIME + f"watch/{show_id}//episode-{episode}-{type_of}",
        ).text
    )

    if match:
        return (
            optopt.jsonlib.loads(match.group(1).replace('\\"', '"'))
            .get("data", {})
            .get("episode", {})
        )

    return {}


def extract_content(
    session,
    content: "iter_episodes",
    show_id: str,
    *,
    api_endpoint: str,
    return_all: bool = SUPERANIME_RETURN_ALL,
):

    for type_of, episode in content:
        api_response = api.fetch_episode(
            session, show_id, episode, translation_type=type_of
        )

        episode_info = api_response.get("episode") or fetch_legacy(
            session, episode, type_of, show_id
        )

        if not episode_info:
            continue

        attrs = {}

        if "notes" in episode_info and episode_info["notes"]:
            attrs.update(title=episode_info["notes"].replace("<note-split>", " // "))

        sources = sorted(
            episode_info["sourceUrls"],
            key=lambda value: value.get("priority", 0),
            reverse=True,
        )

        if not sources:
            continue

        for source in sources:
            if source["type"] == "iframe":

                streams = (
                    session.get(to_clock_json(api_endpoint + source["sourceUrl"]))
                    .json()
                    .get("links")
                )

                if not streams:
                    continue

                for stream_data in streams:
                    if "link" in stream_data and stream_data["link"]:
                        url = stream_data["link"]
                    else:
                        if not stream_data["portData"]["streams"]:
                            continue

                        stream = stream_data["portData"]["streams"][0]

                        url = stream["url"]

                    yield from superscrapers.iter_unpacked_from_packed_hls(
                        session, yarl.URL(url), stream_attribs=attrs
                    )

                    if not return_all:
                        return

            else:
                yield from superscrapers.iter_unpacked_from_packed_hls(
                    session, yarl.URL(source["sourceUrl"]), stream_attribs=attrs
                )
                if not return_all:
                    return


def fetcher(session, url: "str", check, match):

    api_endpoint = (
        session.get(ALLANIME + "getVersion").json().get("episodeIframeHead", "")
    )

    available_episodes = api.fetch_show_info(
        session,
        match.group(1),
    ).get("availableEpisodesDetail", {})

    for episode, content in iter_episodes(available_episodes):

        if check(episode):
            yield partial(
                lambda session, content, show_id: list(
                    extract_content(
                        session, content, show_id, api_endpoint=api_endpoint
                    )
                ),
                session,
                content,
                match.group(1),
            ), episode


def metadata_fetcher(session, url: "str", match):

    anime_name = api.fetch_show_info(
        session,
        match.group(1),
    ).get("name", "")

    return {"titles": [anime_name]}
