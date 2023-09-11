import json
from functools import lru_cache

import regex
import yarl

from .utils import decipher_salted_aes

CONTENT_ID_REGEX = regex.compile(r"embed-6/([^?#&/.]+)")

SALT_SECRET_ENDPOINT = "https://github.com/enimax-anime/key/raw/e6/key.txt"


@lru_cache()
def get_associative_key(session, endpoint):
    return session.get(endpoint).json()


def extract(session, url, **opts):
    url = yarl.URL(url)

    ajax_response = session.get(
        f"https://{url.host}/embed-2/ajax/e-1/getSources",
        params={"id": url.name},
    )

    sources = ajax_response.json()

    key_finders = None
    encrypted: bool = sources["encrypted"]

    if encrypted:
        key_finders = get_associative_key(session, SALT_SECRET_ENDPOINT)

    subtitles = [
        _.get("file") for _ in sources.get("tracks") if _.get("kind") == "captions"
    ]

    if encrypted:
        retval = json.loads(decipher_salted_aes(sources["sources"], key_finders))

    else:
        retval = sources["sources"]

    def yielder():
        for _ in retval:
            yield {
                "stream_url": _["file"],
                "subtitle": subtitles,
            }

    return list(yielder())
