import functools
from functools import partial

import regex

from ....config import ANIMTIME
from ...helpers import construct_site_based_regex

CONTENT_RE = regex.compile(r't\[t\.(?P<name>.+?)=(?P<id>\d+)\]="\1"')
REGEX = construct_site_based_regex(ANIMTIME, extra_regex=r"/title/([^/?&]+)")

MAIN_JS_FILE = "main.0eab142b791320871345.js"


def get_content(content_id, js_content):
    for content in CONTENT_RE.finditer(js_content):
        if content.group("id") == content_id:
            return content.group("name")


@functools.lru_cache()
def get_js_content(session):
    return session.get(ANIMTIME + MAIN_JS_FILE).text


def fetcher(session, url, check, match):

    content = get_js_content(session)[374391:]

    anime = get_content(match.group(1), content)

    if anime is None:
        return

    episode_count = int(
        regex.search(rf"Ld\[Kd\.{regex.escape(anime)}\]=(\d+)", content).group(1)
    )

    constructor, end = regex.search(
        regex.escape(f"Fd[Kd.{anime}]=function(t){{return")
        + '"(.+?)"'
        + regex.escape("+t+")
        + r'"(.+?)"\}',
        content,
    ).groups()

    for episode in range(1, episode_count + 1):
        if check(episode):
            yield partial(
                lambda x: [{"stream_url": x, "headers": {"referer": ANIMTIME}}],
                constructor + "{:03d}".format(episode) + end,
            ), episode


def metadata_fetcher(session, url, match):
    content = get_js_content(session)[374391:]

    anime_name = get_content(match.group(1), content)

    if anime_name is not None:
        anime_name = " ".join(regex.split(r"(?=[A-Z])", anime_name)).strip()

    return {"titles": [anime_name]}
