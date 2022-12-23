from collections import defaultdict
from functools import partial

import yarl

from ....config import ALLANIME, SUPERANIME_RETURN_ALL, SUPERANIME_TYPE_OF
from ...helpers import construct_site_based_regex, optopt

REGEX = construct_site_based_regex(ALLANIME, extra_regex=r"/anime/([^?&/]+)")

SOURCE_EMBED_REGEX = optopt.regexlib.compile(
    r'<iframe id="episode-frame" .+? src="(.+?)"'
)
SOURCE_URLS = optopt.regexlib.compile(
    r'sourceUrl[:=]"(?P<url>.+?)"[;,](?:.+?\.)?priority[:=](?P<priority>.+?)[;,](?:.+?\.)?sourceName[:=](?P<name>.+?)[,;]'
)
EPISODES_REGEX = optopt.regexlib.compile(r'\\"availableEpisodesDetail\\":({.+?})')
TITLES_REGEX = optopt.regexlib.compile(r'<span class="mr-1">(.+?);?</span>')

EMBED_RESOLVERS = {
    '"Ok"': "okru",
    '"Vid-mp4"': "gogoanime",
    '"Mp4"': "mp4upload",
    '"Sl-mp4"': "streamlare",
    '"Ss-Hls"': "streamsb",
}


def iter_episodes(
    episode_dictionary: dict,
    anime_page_url: str,
    *,
    selected_type_of: str = SUPERANIME_TYPE_OF,
):
    episodes = defaultdict(list)

    for type_of, episode_numbers in episode_dictionary.items():
        if type_of != selected_type_of:
            continue

        for episode in episode_numbers:
            episodes[int(episode) if episode.isdigit() else 0].append(
                (
                    f"Episode {episode}",
                    anime_page_url + "/episodes/{}/{}".format(type_of, episode),
                )
            )

    yield from sorted(episodes.items(), key=lambda x: x[0])


def unicode_escape(string: str):
    return string.encode("utf-8").decode("unicode_escape")


def to_json_url(url: "yarl.URL"):
    return url.with_name(url.name + ".json").with_query(url.query)


def iter_prioritised(session, urls, *, title):

    for url, (priority, name) in urls:
        data = session.get(url.human_repr()).text

        if data == "Wrongerror":
            continue

        json_parsed = optopt.jsonlib.loads(data)["links"]

        for link in json_parsed:

            stream_attr = {}

            if "resolution" in link:
                stream_attr["quality"] = link["resolution"]

            if "subtitles" in link:
                stream_attr["subtitles"] = [_["src"] for _ in link["subtitles"]]

            yield {
                "stream_url": link.get("link"),
                "title": title,
                **stream_attr,
            }


def extract_content(
    session,
    content: "iter_episodes",
    *,
    api_endpoint: "yarl.URL",
    return_all: bool = SUPERANIME_RETURN_ALL,
):

    for title, url in content:

        direct_providers = set()
        embed_providers = set()

        content_page = session.get(url).text

        has_on_embed = SOURCE_EMBED_REGEX.search(content_page)

        if has_on_embed:
            direct_providers.add(
                (to_json_url(yarl.URL(has_on_embed.group(1))), (0, "embed"))
            )
        else:
            for source_urls in SOURCE_URLS.finditer(content_page):

                raw_url = unicode_escape(source_urls.group(1))
                parsed_url = yarl.URL(raw_url)

                priority, name = source_urls.group("priority", "name")

                if parsed_url.host is None:
                    parsed_url = api_endpoint.join(to_json_url(parsed_url))
                    direct_providers.add((parsed_url, (priority, name)))
                else:
                    embed_providers.add((parsed_url, (priority, name)))

        iterator = iter_prioritised(
            session, sorted(direct_providers, key=lambda x: x[1][0]), title=title
        )

        if return_all:
            yield from iterator
        else:
            child = next(iterator, None)

            if child is not None:
                yield child


def fetcher(session, url: "str", check, match):
    anime_url = ALLANIME + f"anime/{match.group(1)}"

    api_endpoint = yarl.URL(
        session.get(ALLANIME + "getVersion").json().get("episodeIframeHead", "")
    )

    for episode, content in iter_episodes(
        optopt.jsonlib.loads(
            EPISODES_REGEX.search(session.get(anime_url).text)
            .group(1)
            .replace('\\"', '"')
        ),
        anime_url,
    ):
        if check(episode):
            yield partial(
                lambda session, content: list(
                    extract_content(session, content, api_endpoint=api_endpoint)
                ),
                session,
                content,
            ), episode


def metadata_fetcher(session, url: "str", match):
    anime_url = ALLANIME + f"anime/{match.group(1)}"

    return {"titles": TITLES_REGEX.findall(session.get(anime_url).text)}
