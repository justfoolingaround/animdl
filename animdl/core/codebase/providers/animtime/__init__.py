from functools import partial

import regex

from ....config import ANIMTIME
from ...helper import construct_site_based_regex

CONTENT_RE = regex.compile(r"t\.(\w+)=([0-9]+)")
REGEX = construct_site_based_regex(ANIMTIME, extra_regex=r"/title/([^/?&]+)")


def get_content(url, js_content):
    content_slug = REGEX.match(url).group(1)
    for match in CONTENT_RE.finditer(js_content):
        if match.group(2) == content_slug:
            return match


def fetcher(session, url, check, match):

    content = session.get(
        ANIMTIME + "/main.fe2f7537e4a9d7929fe6.js", headers={"range": "bytes=386216-"}
    ).text

    anime = get_content(url, content)
    episodes = int(
        regex.search(
            r"zd.*?\[tm\.{}\]=(\d+)".format(regex.escape(anime.group(1))), content
        ).group(1)
    )
    constructor, end = regex.search(
        r'\[tm\.{}\]=function\(t\){{return"(.+?)"\+t\+"(.+?)"'.format(
            regex.escape(anime.group(1))
        ),
        content,
    ).groups()
    for episode in range(1, episodes + 1):
        if check(episode):
            yield partial(
                lambda x: [{"stream_url": x, "headers": {"referer": ANIMTIME}}],
                constructor + "{:03d}".format(episode) + end,
            ), episode
