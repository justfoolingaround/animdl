from functools import partial

import yarl

from ....config import TWIST
from ...helper import construct_site_based_regex, parse_from_content
from .stream_url import *

REGEX = construct_site_based_regex(TWIST, extra_regex=r"/a/([^?&/]+)")


def fetcher(session, url, check, match):
    anime_name = match.group(1)

    for episode, stream in sorted(
        iter_episodes(session, anime_name), key=lambda k: k[0]
    ):
        if check(episode):
            yield partial(
                lambda s: [
                    parse_from_content(
                        yarl.URL(s),
                        name_processor=lambda u: u.name,
                        stream_url_processor=lambda u: u.human_repr(),
                        overrides={"headers": {"referer": "https://twist.moe/"}},
                        episode_parsed=True,
                    )
                ],
                stream,
            ), episode
