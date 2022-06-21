from base64 import b64decode
from hashlib import md5

from Cryptodome.Cipher import AES

TWISTMOE_SECRET = b"267041df55ca2b36f2e322d05ee2c9cf"

TWISTMOE_CDN = "https://{}cdn.twist.moe"
TWISTMOE_API = "https://api.twist.moe/api/anime/"


def unpad_content(content):
    return content[
        : -(content[-1] if isinstance(content[-1], int) else ord(content[-1]))
    ]


def generate_key(salt: bytes, *, output=48):

    key = md5(TWISTMOE_SECRET + salt).digest()
    current_key = key

    while len(current_key) < output:
        key = md5(key + TWISTMOE_SECRET + salt).digest()
        current_key += key

    return current_key[:output]


def decipher(encoded_url: str):

    s1 = b64decode(encoded_url.encode("utf-8"))
    assert s1.startswith(b"Salted__"), "Not a salt."
    key = generate_key(s1[8:16])
    return (
        unpad_content(AES.new(key[:32], AES.MODE_CBC, key[32:]).decrypt(s1[16:]))
        .decode("utf-8", "ignore")
        .lstrip(" ")
    )


def api(session, endpoint, content_slug):
    return session.get(
        TWISTMOE_API + content_slug + endpoint,
        headers={"x-access-token": "0df14814b9e590a1f26d3071a4ed7974"},
    )


def iter_episodes(session, content_slug):

    ongoing = api(session, "/", content_slug).json().get("ongoing")

    source_base = TWISTMOE_CDN.format("air-" if ongoing else "")

    episodes_page = api(session, "/sources", content_slug)

    if episodes_page.status_code >= 400:
        return

    for episode in api(session, "/sources", content_slug).json():
        yield episode.get("number", 0), source_base + decipher(episode.get("source"))
