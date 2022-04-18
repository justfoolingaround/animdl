import base64
import json

import functools
import regex
import yarl
from Cryptodome.Cipher import AES
from binascii import unhexlify

CUSTOM_PADDER = "\x08\x0e\x03\x08\t\x03\x04\t"
ENCRYPTION_KEYS = "https://raw.githubusercontent.com/justfoolingaround/animdl-provider-benchmarks/master/api/gogoanime.json"


def get_quality(url_text):
    match = regex.search(r"(\d+) P", url_text)

    if not match:
        return None

    return int(match.group(1))


def pad(data):
    return data + chr(len(data) % 16) * (16 - len(data) % 16)


def aes_encrypt(data: str, *, key, iv):
    return base64.b64encode(
        AES.new(key, AES.MODE_CBC, iv=iv).encrypt(pad(data).encode())
    )


def aes_decrypt(data: str, *, key, iv):
    return AES.new(key, AES.MODE_CBC, iv=iv).decrypt(base64.b64decode(data))


@functools.lru_cache()
def get_encryption_keys(session):
    return {
        _: unhexlify(__.encode())
        for _, __ in session.get(ENCRYPTION_KEYS).json().items()
    }


def extract(session, url, **opts):
    """
    Extract content off of GogoAnime.

    Next time you dare change gogo, I'll add a trace to your
    stupid site's JS and automate the Python code conversion
    from there.

    Now, now, there's no fun in the games where your opponent
    is faster than you by a landslide, is it?

    Resistance is futile.
    """
    parsed_url = yarl.URL(url)
    next_host = "https://{}/".format(parsed_url.host)

    keys = get_encryption_keys(session)
    content_id = parsed_url.query.get("id")

    response = session.get(
        "{}encrypt-ajax.php".format(next_host),
        params={
            "id": aes_encrypt(content_id, key=keys["key"], iv=keys["iv"]).decode(),
            "alias": content_id,
        },
        headers={"x-requested-with": "XMLHttpRequest", "referer": next_host},
    )
    content = json.loads(
        aes_decrypt(
            response.json().get("data"), key=keys["second_key"], iv=keys["iv"]
        ).strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10")
    )

    def yielder():
        for origin in content.get("source"):
            yield {
                "stream_url": origin.get("file"),
                "quality": get_quality(origin.get("label", "")),
                "headers": {"referer": next_host},
            }

        for backups in content.get("source_bk"):
            yield {
                "stream_url": backups.get("file"),
                "quality": get_quality(origin.get("label", "")),
                "headers": {"referer": next_host},
            }

    return list(yielder())
