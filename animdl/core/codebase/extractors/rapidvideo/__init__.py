import json
from functools import lru_cache

import regex
import yarl

from .utils import decipher_salted_aes

CONTENT_ID_REGEX = regex.compile(r"embed-6/([^?#&/.]+)")

SALT_SECRET_ENDPOINT = "https://github.com/enimax-anime/key/raw/e6/key.txt"


@lru_cache()
def get_associative_key(session, endpoint):
    return session.get(endpoint).text


def extract(session, url, **opts):

    url = yarl.URL(url)

    ajax_response = session.get(
        f"https://{url.host}/ajax/embed-6/getSources",
        params={"id": url.name},
    )

    sources = ajax_response.json()

    salt_secret = None
    encrypted = sources["encrypted"]

    if encrypted:
        salt_secret = get_associative_key(session, SALT_SECRET_ENDPOINT).encode("utf-8")

    subtitles = [
        _.get("file") for _ in sources.get("tracks") if _.get("kind") == "captions"
    ]

    if encrypted:
        retval = json.loads(
            decipher_salted_aes(sources["sources"], salt_secret)
        ) + json.loads(decipher_salted_aes(sources["sourcesBackup"], salt_secret))

    else:
        retval = sources["sources"] + sources["sourcesBackup"]

    def yielder():
        for _ in retval:
            yield {
                "stream_url": _["file"],
                "subtitle": subtitles,
            }

    return list(yielder())
