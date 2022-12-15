import json
import time
from base64 import b64decode, b64encode
from functools import partial

import lxml.html as htmlparser
import regex
import yarl

from .hardstream import get_hardstream_generator, hard_urls

ID_MATCHER = regex.compile(r"\?id=([^&]+)")
EMBED_URL_BASE = "https://animixplay.to/api/cW9"
EMBED_M3U8_MATCHER = regex.compile(r"player\.html?[^#]*#([^#]+)")
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
            url = url.replace(key, item)
    return url


def extract_from_url(embed_url):

    on_url = EMBED_M3U8_MATCHER.search(embed_url) or EMBED_B64_MATCHER.search(embed_url)

    if not on_url:
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
        return extract_from_url(on_site.group(1))

    return extract_from_url(str(embed_page.url))


def get_stream_url(session, data_url):

    component = yarl.URL(data_url)

    if component.host == "www.dailymotion.com":
        return [{"stream_url": data_url, "further_extraction": ("dailymotion", {})}]

    content_id = component.query.get("id")

    if content_id:
        return extract_from_embed(
            session,
            EMBED_URL_BASE
            + b64encode(
                "{}LTXs3GrU8we9O{}".format(
                    content_id,
                    b64encode(content_id.encode()).decode(),
                ).encode()
            ).decode(),
        ) or [
            {
                "stream_url": data_url,
                "further_extraction": ("gogoplay", {}),
            }
        ]

    return extract_from_url(data_url)


def fetcher(session, url, check, match):

    slug = match.group(1)

    if slug in hard_urls:
        generator = get_hardstream_generator(session, slug)
        if generator is not None:
            yield from generator
            return

    data = json.loads(
        htmlparser.fromstring(session.get(url).content)
        .cssselect("#epslistplace")[0]
        .text
    )

    for value in range(int(data.get("eptotal"))):
        if check(value + 1):
            yield partial(get_stream_url, session, data[str(value)]), value + 1
