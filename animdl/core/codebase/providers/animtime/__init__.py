import functools
from functools import partial

from animdl.utils.optopt import regexlib

from ....config import ANIMTIME
from ...helpers import construct_site_based_regex

CONTENT_RE = regexlib.compile(r't\[t\.(?P<name>.+?)=(?P<id>\d+)\]="\1"')
REGEX = construct_site_based_regex(ANIMTIME, extra_regex=r"/title/([^/?&]+)")

MAIN_JS_RE = regexlib.compile(r'<script src="(main\..+?\.js)".+?>')


def get_content(content_id, js_content):
    for content in CONTENT_RE.finditer(js_content):
        if content.group("id") == content_id:
            return content.group("name")


@functools.lru_cache()
def get_js_content(session):
    content = session.get(ANIMTIME).text
    main_js = MAIN_JS_RE.search(content).group(1)

    return session.get(ANIMTIME + main_js).text


def fetcher(session, url, check, match):

    content = get_js_content(session)[374391:]

    anime = get_content(match.group(1), content)

    if anime is None:
        return

    episode_count = int(
        regexlib.search(rf"Ld\[Kd\.{regexlib.escape(anime)}\]=(\d+)", content).group(1)
    )

    constructor, end = regexlib.search(
        regexlib.escape(f"Fd[Kd.{anime}]=function(t){{return")
        + '"(.+?)"'
        + regexlib.escape("+t+")
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
        anime_name = " ".join(regexlib.split(r"(?=[A-Z])", anime_name)).strip()

    return {"titles": [anime_name]}
