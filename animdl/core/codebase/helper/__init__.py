from collections import defaultdict

import anitopy
import regex


def construct_site_based_regex(site_url, *, extra="", extra_regex=""):
    return regex.compile(
        "(?:https?://)?(?:\\S+\\.)*{}".format(
            regex.escape(
                regex.search(r"(?:https?://)?((?:\S+\.)+[^/]+)/?", site_url).group(1)
            )
            + extra
        )
        + extra_regex
    )


def append_protocol(uri, *, protocol="https"):
    if regex.search(r"^.+?://", uri):
        return uri
    return "{}://{}".format(protocol.rstrip(":/"), uri.lstrip("/"))


def parse_from_content(
    content,
    *,
    name_processor=lambda x: x,
    stream_url_processor=lambda x: x,
    overrides={},
    episode_parsed=False
):

    anitopy_result = anitopy.parse(name_processor(content))

    returnee = {"stream_url": stream_url_processor(content)}
    video_res = anitopy_result.get("video_resolution") or ""

    if not episode_parsed:
        returnee.update({"episode": int(anitopy_result.get("episode_number", 0) or 0)})

    if isinstance(video_res, str):
        stripped = video_res.strip("p")
        if stripped.isdigit():
            returnee.update({"quality": int(stripped)})

    returnee.update(overrides)

    return returnee


def group_episodes(contents):
    grouped = defaultdict(list)
    for r in contents:
        grouped[int(r.pop("episode", 0))].append(r)
    return grouped
