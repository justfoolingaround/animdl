import base64
from functools import partial

import lxml.html as htmlparser
import regex

from ....config import HENTAISTREAM
from ...helper import construct_site_based_regex, uwu

EPISODE_REGEX = regex.compile(r"/\d+/[^&?/]+")

REGEX = construct_site_based_regex(HENTAISTREAM, extra_regex=r"/(anime|\d+)/([^?&/]+)")

QUALITY_MAP = {
    720: "x264.720p.mp4",
    1080: "av1.1080p.webm",
    2160: "av1.2160p.webm",
    4320: "av1.4320p.webm",
}


def get_episodes_page(session, url):
    return (
        htmlparser.fromstring(session.get(url).text)
        .cssselect('li[itemscope] > a[href^="https://hentaistream.moe/anime/"]')[0]
        .get("href")
    )


def extract_from_site(session, episode_url, **opts):

    for embed in htmlparser.fromstring(session.get(episode_url).text).cssselect(
        "iframe"
    ):
        _, content_uri = embed.get("src", "#").split("#")
        base, *_sub = regex.split(r"[;,]", base64.b64decode(content_uri).decode()[4:])

        subtitle = list(base + _ + ".vtt" for _ in _sub)

        stream_meta = {**opts, **({"subtitle": subtitle} if subtitle else {})}

        for quality, suffix in QUALITY_MAP.items():
            stream = base + suffix
            if (
                session.head(stream, headers={"referer": HENTAISTREAM}).status_code
                == 200
            ):
                yield {
                    "quality": quality,
                    "stream_url": stream,
                    "headers": {"referer": HENTAISTREAM},
                    **stream_meta,
                }


def fetcher(session, url, check, match):
    uwu.bypass_ddos_guard(session, HENTAISTREAM)

    if match.group(1).isdigit():
        url = get_episodes_page(session, url)

    for episode_page in htmlparser.fromstring(session.get(url).text).cssselect(
        "li[data-index] > a"
    )[::-1]:
        number, title, date = (
            _.text_content() for _ in episode_page.cssselect('div[class^="epl"]')
        )
        episode_number = int(number) if number.isdigit() else 0

        if check(episode_number):
            yield partial(
                lambda ep, **opts: list(extract_from_site(session, ep, **opts)),
                episode_page.get("href"),
                title="{} ({})".format(title, date),
            ), episode_number
