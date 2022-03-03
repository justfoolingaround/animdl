import base64
import json

import lxml.html as htmlparser
import regex
import yarl
from Cryptodome.Cipher import AES

GOGOANIME_SECRET = b"25716538522938396164662278833288"
GOGOANIME_IV = b"1285672985238393"
CUSTOM_PADDER = "\x08\x0e\x03\x08\t\x03\x04\t"


def get_quality(url_text):
    match = regex.search(r"(\d+) P", url_text)

    if not match:
        return None

    return int(match.group(1))


def pad(data):
    return data + CUSTOM_PADDER[(len(CUSTOM_PADDER) - len(data) % 16) :]


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

    content_info = aes_decrypt(
        htmlparser.fromstring(session.get(url).text)
        .cssselect('[data-name="crypto"]')[0]
        .get("data-value")
    )
    content_id = content_info[: content_info.index(b"&")].decode()

    parsed_url = yarl.URL(url)
    next_host = "https://{}/".format(parsed_url.host)

    response = session.get(
        "{}encrypt-ajax.php".format(next_host),
        params={"id": aes_encrypt(content_id).decode()},
        headers={"x-requested-with": "XMLHttpRequest"},
    )
    content = json.loads(
        aes_decrypt(response.json().get("data"))
        .replace(b'o"<P{#meme":', b'e":[{"file":')
        .decode("utf-8")
        .strip("\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f")
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
