"""
Useless since there is no open-source way to bypass ouo.io (currently).

This is quite slow as it tries to get all the streams at once.
"""

from base64 import b64decode
from functools import partial

import regex

from ....config import ANIMEKAIZOKU
from ...helper import construct_site_based_regex, group_episodes, parse_from_content

REGEX = construct_site_based_regex(ANIMEKAIZOKU, extra_regex=r"/([^?&/]+)")


ON_NEW_TAB = regex.compile(r'openInNewTab\("(.+?)"\)\'><p>Download (.+?)</p>')

ANIMEKAIZOKU_DDL = regex.compile(r"DDL\((.+?), (.+?), '(.+?)', (.+?)\)")

DDL_DIVID = regex.compile(r"glist-(\d+)")
DDL_POSTID = regex.compile(r'"postId":"(\d+)"')


def graceful_ajax(session, data):
    return session.post(
        ANIMEKAIZOKU + "wp-admin/admin-ajax.php",
        headers={"x-requested-with": "XMLHttpRequest", "referer": ANIMEKAIZOKU},
        data=data,
    )


def walk(session, post_id, div_id, tab_id, num, folder):

    loaded_page = graceful_ajax(
        session,
        {
            "action": "DDL",
            "post_id": post_id,
            "div_id": div_id,
            "tab_id": tab_id,
            "num": num,
            "folder": folder,
        },
    ).text

    for match in ANIMEKAIZOKU_DDL.finditer(loaded_page):
        yield from walk(session, post_id, *match.groups())

    for match in ON_NEW_TAB.finditer(loaded_page):
        yield match


def fetcher(session, url, check, match):

    response = session.get(url).text

    div_id = DDL_DIVID.search(response).group(1)
    post_id = DDL_POSTID.search(response).group(1)

    for episode, streams in sorted(
        group_episodes(
            (
                parse_from_content(
                    regex_match,
                    name_processor=lambda m: m.group(2),
                    stream_url_processor=lambda m: (
                        b64decode(m.group(1)).decode("utf-8")
                    ),
                )
                for regex_match in walk(session, post_id, div_id, 2, "", True)
            )
        ).items()
    ):
        if check(episode):
            yield partial(list, streams), episode
