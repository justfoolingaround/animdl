from functools import partial

import lxml.html as htmlparser
import regex

from ....config import NINEANIME
from ...helpers import construct_site_based_regex
from .decipher import decrypt_url

CONTENT_ID_REGEX = regex.compile(r'data-id="(.+?)"')

REGEX = construct_site_based_regex(
    NINEANIME, extra_regex=r"/watch/[^&?/]+\.(?P<slug>[^&?/]+)"
)
TITLES_REGEX = regex.compile(r'<h1 class="title d-title" .+?>(.+?)</h1>')

SOURCES = {
    "41": "vidstream",
    "28": "mycloud",
    "35": "mp4upload",
    "40": "streamtape",
    "43": "videovard",
    "44": "filemoon",
}

DECRYPTION_CODE = "hlPeNwkncH0fq9so"


def fetch_episode(session, data_source):

    response = htmlparser.fromstring(
        session.get(
            NINEANIME + f"ajax/server/list/{data_source.get('data-ids')}"
        ).json()["result"]
    )

    for content_type_container in response.cssselect("div[data-type]"):

        for servers in content_type_container.cssselect("ul > li[data-sv-id]"):

            source = SOURCES[servers.get("data-sv-id")]

            content_url = decrypt_url(
                session.get(
                    NINEANIME + f"ajax/server/{servers.get('data-link-id')}/"
                ).json()["result"]["url"],
                DECRYPTION_CODE,
            )
            yield {
                "stream_url": content_url,
                "further_extraction": (
                    source,
                    {"headers": {"referer": NINEANIME}},
                ),
                "title": f"Episode {data_source.get('data-num')}, {content_type_container.get('data-type').upper()}",
            }


def fetcher(session, url, check, match):

    content_id = CONTENT_ID_REGEX.search(session.get(url).text).group(1)

    for data_source in htmlparser.fromstring(
        session.get(
            NINEANIME + f"ajax/episode/list/{content_id}",
        ).json()["result"]
    ).cssselect("a[data-num]"):
        yield partial(
            lambda data_source: list(fetch_episode(session, data_source)),
            data_source,
        ), data_source.get("data-num")


def metadata_fetcher(session, url, match):

    response = session.get(url).text

    return {"titles": TITLES_REGEX.findall(response)}
