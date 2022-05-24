import regex

from ...providers.nineanime.decipher import cipher_keyed, encrypt

EMBED_URL_REGEX = regex.compile(r"(.+?/)(?:e(?:mbed)?)/([a-zA-Z0-9]+)")

BASE64_TABLE = "0wMrYU+ixjJ4QdzgfN2HlyIVAt3sBOZnCT9Lm7uFDovkb/EaKpRWhqXS5168ePcG"


def extract(session, url, **opts):

    match = EMBED_URL_REGEX.search(url)
    host, slug = match.group(1, 2)

    vidstream_info = session.get(
        "{}info/{}".format(
            host,
            encrypt(
                cipher_keyed("LCbu3iYC7ln24K7P", encrypt(slug, table=BASE64_TABLE)),
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
