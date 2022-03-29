import base64
import json

import lxml.html as htmlparser
import regex
import yarl
from Cryptodome.Cipher import AES

GOGOANIME_SECRET = b"63976882873559819639988080820907"
GOGOANIME_IV = b"4770478969418267"
CUSTOM_PADDER = "\x08\x0e\x03\x08\t\x03\x04\t"


def get_quality(url_text):
    match = regex.search(r"(\d+) P", url_text)

    if not match:
        return None

    return int(match.group(1))


def pad(data):
    return data + chr(len(data) % 16) * (16 - len(data) % 16)


def aes_encrypt(data: str):
    return base64.b64encode(
        AES.new(GOGOANIME_SECRET, AES.MODE_CBC, iv=GOGOANIME_IV).encrypt(
            pad(data).encode()
        )
    )


def aes_decrypt(data: str):
    return AES.new(GOGOANIME_SECRET, AES.MODE_CBC, iv=GOGOANIME_IV).decrypt(
        base64.b64decode(data)
    )


def extract(session, url, **opts):
    """
    Extract content off of GogoAnime.
    """
    parsed_url = yarl.URL(url)
    next_host = "https://{}/".format(parsed_url.host)

    response = session.get(
        "{}encrypt-ajax.php".format(next_host),
        params={"id": aes_encrypt(parsed_url.query.get("id")).decode()},
        headers={"x-requested-with": "XMLHttpRequest"},
    )
    content = json.loads(
        aes_decrypt(response.json().get("data")).strip(
            b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"
        )
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
