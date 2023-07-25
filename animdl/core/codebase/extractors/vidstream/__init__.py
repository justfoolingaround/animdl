import regex

from ...providers.nineanime.decipher import generate_vrf_from_content_id

EMBED_URL_REGEX = regex.compile(r"(.+?)/(?:e(?:mbed)?)/([a-zA-Z0-9]+)")
ID_KEY = b"FtFyeHeWL36bANDy"
CHAR_SUBST_OFFSETS = [-6, 3, 3, -5, 2, -6]


def extract(session, url, **opts):
    match = EMBED_URL_REGEX.search(url)
    host = match.group(1)
    video_id = generate_vrf_from_content_id(
        match.group(2), offsets=CHAR_SUBST_OFFSETS, key=ID_KEY, reverse_later=False
    )

    vidstream_info = session.get(
        f"{host}/mediainfo/{video_id}", headers={"referer": url}
    )

    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json()["result"].get("sources", [])
    ]
