from collections import defaultdict
from functools import partial

import yarl

from ....config import ALLANIME, SUPERANIME_RETURN_ALL, SUPERANIME_TYPE_OF
from ...helpers import construct_site_based_regex, optopt, superscrapers

REGEX = construct_site_based_regex(ALLANIME, extra_regex=r"/anime/([^?&/]+)")

EPISODES_REGEX = optopt.regexlib.compile(r'\\"availableEpisodesDetail\\":({.+?})')
TITLES_REGEX = optopt.regexlib.compile(r'<span class="mr-1">(.+?);?</span>')

ALLANIME_GQL_EXTENSIONS = {
    "persistedQuery": {
        "version": 1,
    }
}

ALLANIME_GQL_EPISODE_QUERY_EXTENSIONS = optopt.jsonlib.dumps(
    {
        "persistedQuery": {
            **ALLANIME_GQL_EXTENSIONS["persistedQuery"].copy(),
            "sha256Hash": "1f0a5d6c9ce6cd3127ee4efd304349345b0737fbf5ec33a60bbc3d18e3bb7c61",
        }
    }
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


def extract_content(
    session,
    content: "iter_episodes",
    show_id: str,
    *,
    api_endpoint: str,
    return_all: bool = SUPERANIME_RETURN_ALL,
):

    for type_of, episode in content:

        api_response = session.get(
            "https://api.allanime.co/allanimeapi",
            params={
                "variables": optopt.jsonlib.dumps(
                    {
                        "showId": show_id,
                        "translationType": type_of,
                        "episodeString": episode,
                    }
                ),
                "extensions": ALLANIME_GQL_EPISODE_QUERY_EXTENSIONS,
            },
        ).json()

        episode_info = api_response["data"]["episode"]

        attrs = {}

        if "notes" in episode_info and episode_info["notes"]:
            attrs.update(title=episode_info["notes"].replace("<note-split>", " // "))

        sources = sorted(
            api_response["data"]["episode"]["sourceUrls"],
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
    anime_url = ALLANIME + f"anime/{match.group(1)}"

    api_endpoint = (
        session.get(ALLANIME + "getVersion").json().get("episodeIframeHead", "")
    )

    for episode, content in iter_episodes(
        optopt.jsonlib.loads(
            EPISODES_REGEX.search(session.get(anime_url).text)
            .group(1)
            .replace('\\"', '"')
        ),
    ):

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
    anime_url = ALLANIME + f"anime/{match.group(1)}"

    return {"titles": TITLES_REGEX.findall(session.get(anime_url).text)}
