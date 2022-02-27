import json
import logging
import time
from base64 import b64decode, b64encode
from functools import partial

import lxml.html as htmlparser
import regex

animixplay_logger = logging.getLogger("provider:animixplay")

ID_MATCHER = regex.compile(r"\?id=([^&]+)")
EMBED_URL_BASE = "https://animixplay.to/api/live"
EMBED_M3U8_MATCHER = regex.compile(r"player\.html[?#](.+?)#")
EMBED_B64_MATCHER = regex.compile(r"#(aHR0[^#]+)")
EMBED_VIDEO_MATCHER = regex.compile(r'iframesrc="(.+?)"')

URL_ALIASES = {
    "bestanimescdn": "omega.kawaiifucdn.xyz/anime3",
    "anicdn.stream": "gogocdn.club",
    "ssload.info": "gogocdn.club",
}


def url_update(url):
    for key, item in URL_ALIASES.items():
        if key in url:
            animixplay_logger.debug(
                "Replacing {!r} to {!r} in {!r}.".format(key, item, url)
            )
            url = url.replace(key, item)
    return url


def extract_from_url(embed_url):
    on_url = EMBED_M3U8_MATCHER.search(embed_url) or EMBED_B64_MATCHER.search(embed_url)

    if not on_url:
        animixplay_logger.debug(
            "Failed to find stream on {!r}, will fallback to API based m3u8.".format(
                embed_url
            )
        )
        return []

    return [{"stream_url": url_update(b64decode(on_url.group(1)).decode())}]


def extract_from_embed(session, embed_url):
    embed_page = session.get(embed_url)

    while embed_page.status_code == 429:
        embed_page = session.get(embed_url)
        time.sleep(2.5)

    if embed_page.status_code == 403:
        return []

    on_site = EMBED_VIDEO_MATCHER.search(embed_page.text)

    if on_site:
        animixplay_logger.debug(
            "Regex matched a video on the site: {!r}, extracting.".format(on_site)
        )
        return extract_from_url(on_site.group(1))

    return extract_from_url(str(embed_page.url))


def get_stream_url(session, data_url):
    content_id = ID_MATCHER.search(data_url)

    if content_id:
        return extract_from_embed(
            session,
            EMBED_URL_BASE
            + b64encode(
                "{}LTXs3GrU8we9O{}".format(
                    content_id.group(1),
                    b64encode(content_id.group(1).encode()).decode(),
                ).encode()
            ).decode(),
        ) or [
            {
                "stream_url": "https://gogoplay1.com/streaming.php?id={}".format(
                    content_id.group(1)
                ),
                "further_extraction": ("gogoplay", {}),
            }
        ]

    return extract_from_url(data_url)


def fetcher(session, url, check, match):
    data = json.loads(
        htmlparser.fromstring(session.get(url).content)
        .cssselect("#epslistplace")[0]
        .text
    )

    for value in range(data.get("eptotal")):
        if check(value + 1):
            yield partial(get_stream_url, session, data[str(value)]), value + 1
