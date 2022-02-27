from functools import partial

import lxml.html as htmlparser
import yarl

from ....config import ANIMEOUT
from ...helper import construct_site_based_regex, group_episodes, parse_from_content

REGEX = construct_site_based_regex(ANIMEOUT, extra_regex=r"/([^?&/]+)")


def animeout_stream_url(url: "yarl.URL") -> str:
    return "https://public.animeout.xyz/" + url.with_scheme("").human_repr().lstrip("/")


def fetcher(session, url, check, match):
    animeout_page = session.get(url)
    parsed = htmlparser.fromstring(animeout_page.text)

    downloadables = (
        yarl.URL(_.get("href"))
        for _ in parsed.cssselect('.article-content a[href$="mkv"]')
        if "Download" in _.text_content()
    )

    for episode, content in sorted(
        (
            group_episodes(
                parse_from_content(
                    content,
                    name_processor=lambda c: c.name,
                    stream_url_processor=animeout_stream_url,
                )
                for content in downloadables
            ).items()
        ),
        key=lambda x: x[0],
    ):
        if check(episode):
            yield partial(list, content), episode
