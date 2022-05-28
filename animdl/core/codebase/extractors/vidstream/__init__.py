import functools

import regex

from ...providers.nineanime.decipher import cipher_keyed, encrypt

EMBED_URL_REGEX = regex.compile(r"(.+?/)(?:e(?:mbed)?)/([a-zA-Z0-9]+)")

BASE64_TABLE = "51wJ0FDq/UVCefLopEcmK3ni4WIQztMjZdSYOsbHr9R2h7PvxBGAuglaN8+kXT6y"


CIPHER_KEY_API = "https://raw.githubusercontent.com/justfoolingaround/animdl-provider-benchmarks/master/api/selgen.json"


@functools.lru_cache()
def get_ciper_key(session):
    return session.get(CIPHER_KEY_API).json()["cipher_key"]


def extract(session, url, **opts):
    """
    `CIPHER_KEY_API` created by very shit dev, wonder who that is.

    In any case 9Anime, still wanna play tag?
    """

    match = EMBED_URL_REGEX.search(url)
    host, slug = match.group(1, 2)

    cipher_key = get_ciper_key(session)

    if cipher_key is None:
        return []

    vidstream_info = session.get(
        "{}info/{}".format(
            host,
            encrypt(
                cipher_keyed(cipher_key, encrypt(slug, table=BASE64_TABLE)),
                table=BASE64_TABLE,
            ).replace("/", "_"),
        ),
    )

    if vidstream_info.status_code == 404:
        return []

    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json()["data"].get("media", {}).get("sources", [])
    ]
