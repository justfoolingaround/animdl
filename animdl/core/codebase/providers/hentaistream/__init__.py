from functools import partial

import lxml.html as htmlparser
import regex

from ....config import HENTAISTREAM
from ...helpers import construct_site_based_regex

EPISODE_REGEX = regex.compile(r"/\d+/[^&?/]+")
TITLES_REGEX = regex.compile(r'<h1 class="entry-title" itemprop="name">(.+?)</h1>')


REGEX = construct_site_based_regex(HENTAISTREAM, extra_regex=r"/hentai/([^?&/]+)")

EXTRACTOR_REGEX = regex.compile(r"src: '(.+?)',\s+type: '.+?',\s+size: (\d+),")
SUBTITLE_URL_REGEX = regex.compile(r"subUrl: '(.+?)'")


def fetch_streams(session, episode_url, **opts):
    episode_page = session.get(HENTAISTREAM + episode_url[1:]).text
    subtitles = SUBTITLE_URL_REGEX.findall(episode_page)

    for url, size in EXTRACTOR_REGEX.findall(episode_page):
        yield {
            "stream_url": url,
            "quality": int(size),
            "headers": {"referer": HENTAISTREAM},
            "subtitle": subtitles,
        }


def fetcher(session, url, check, match):
    response = session.get(match.group(0))
    episode_page = htmlparser.fromstring(response.text)

    episode_id = episode_page.cssselect("input#e_id")[0].get("value")
    csrf = response.cookies.get("XSRF-TOKEN")

    data = session.post(
        HENTAISTREAM + "player/api",
        json={
            "episode_id": episode_id,
        },
        headers={
            "x-xsrf-token": csrf.replace("%3D", "="),
        },
    ).json()

    resolutions = (1080, 720)

    if data["resolution"] == "4k":
        resolutions = (2160,) + resolutions

    yield partial(
        lambda _: _,
        [
            {
                "title": data["title"],
                "stream_url": data["stream_domains"][-1]
                + "/"
                + data["stream_url"]
                + f"/{resolution}/manifest.mpd",
                "subtitle": [
                    data["stream_domains"][-1] + "/" + data["stream_url"] + f"/eng.ass",
                ],
                "quality": resolution,
            }
            for resolution in resolutions
        ],
    ), 1


def metadata_fetcher(session, url, match):
    page = htmlparser.fromstring(session.get(match.group(0)).text)
    return {"titles": page.cssselect("h1.leading-tight")[0].text_content().strip()}
