import functools
import json
from base64 import b64encode
from urllib.parse import quote
from Cryptodome.Cipher import ARC4

import regex

from ...providers.nineanime.decipher import char_subst

EMBED_URL_REGEX = regex.compile(r"(.+?)/(?:e(?:mbed)?)/([a-zA-Z0-9]+)")
ID_KEY = b"FtFyeHeWL36bANDy"
CHAR_SUBST_OFFSETS = [-6, 3, 3, -5, 2, -6]

def mediainfo_id(vid_id):
    result = quote(vid_id)
    result = ARC4.new(ID_KEY).encrypt(result.encode())
    result = b64encode(result).decode()
    result = result[::-1]
    result = char_subst(result, CHAR_SUBST_OFFSETS)
    result = b64encode(result.encode()).decode()
    return result

def extract(session, url, **opts):
    match = EMBED_URL_REGEX.search(url)
    host = match.group(1)
    vid_id = match.group(2)

    vidstream_info = session.get(
        f"{host}/mediainfo/{mediainfo_id(vid_id)}",
        headers={'referer': url}
    )

    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json()["result"].get("sources", [])
    ]
