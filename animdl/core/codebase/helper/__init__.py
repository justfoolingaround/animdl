from collections import defaultdict
from typing import Callable, DefaultDict, Dict, List, TypeVar

import anitopy
import regex

content_type = TypeVar("content_type")


def construct_site_based_regex(
    site_url: "str", *, extra: "str" = "", extra_regex: "str" = ""
):
    return regex.compile(
        "(?:https?://)?(?:\\S+\\.)*{}".format(
            regex.escape(
                regex.search(r"(?:https?://)?((?:\S+\.)+[^/]+)/?", site_url).group(1)
            )
            + extra
        )
        + extra_regex
    )


def append_protocol(uri: "str", *, protocol: "str" = "https"):

    if regex.search(r"^.+?://", uri):
        return uri
    return "{}://{}".format(protocol.rstrip(":/"), uri.lstrip("/"))


def parse_from_content(
    content: "content_type",
    *,
    name_processor: Callable[[content_type], str] = lambda x: x,
    stream_url_processor: Callable[[content_type], str] = lambda x: x,
    overrides: Dict = {},
    episode_parsed: bool = False
):

    anitopy_result = anitopy.parse(name_processor(content))

    returnee = {"stream_url": stream_url_processor(content)}
    video_res = anitopy_result.get("video_resolution") or ""

    if not episode_parsed:

        episode_number = anitopy_result.get("episode_number", 0)

        if isinstance(episode_number, list):
            episode_number = episode_number[0]

        returnee.update({"episode": int(episode_number or 0)})

    if isinstance(video_res, str):
        stripped = video_res.strip("p")
        if stripped.isdigit():
            returnee.update({"quality": int(stripped)})

    returnee.update(overrides)

    return returnee


def group_episodes(
    contents: "List[Dict[str, str]]",
) -> "DefaultDict[int, List[Dict[str, str]]]":
    grouped = defaultdict(list)
    for content in contents:
        grouped[int(content.pop("episode", 0))].append(content)
    return grouped
