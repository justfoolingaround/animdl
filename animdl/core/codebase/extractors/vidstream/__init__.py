import functools
import json
from base64 import b64decode

import regex

from ...providers.nineanime import decipher

EMBED_URL_REGEX = regex.compile(r"(.+?/)(?:e(?:mbed)?)/([a-zA-Z0-9]+)")

SIMPLE_OPERATE_REGEX = regex.compile(r"[0-9]+\s+.+?\s+[0-9]+")


CIPHER_ALGORITHM_DATA_ENDPOINT = (
    "https://raw.githubusercontent.com/AnimeJeff/Overflow/main/syek"
)


def isolated_eval(code, *, builtins=None):
    try:
        return eval(code, {"__builtins__": builtins or {}}, {})
    except Exception:
        return None


@functools.lru_cache()
def get_ciper_algorithm(session):
    return json.loads(
        b64decode(
            b64decode(b64decode(session.get(CIPHER_ALGORITHM_DATA_ENDPOINT).content))
        ).decode()
    )


def string_encrypt(text):
    def repl(match):
        value = ord(match.group(0)) + 13
        return chr(
            value if (90 if ord(match.group(0)) <= 90 else 122) >= value else value - 26
        )

    return regex.sub(r"[a-zA-Z]", repl, text)


def conditional_encrypt(content, steps, b64_table):

    for _ in steps:
        if _ == "o":
            content = decipher.encrypt(content, table=b64_table).replace("/", "_")

        if _ == "s":
            content = string_encrypt(content)

        if _ == "a":
            content = content[::-1]

    return content


def extract(session, url, **opts):

    match = EMBED_URL_REGEX.search(url)
    algorithm = get_ciper_algorithm(session)

    b64_table = algorithm["encryptKey"]

    content_id = decipher.encrypt(
        decipher.cipher_keyed(algorithm["cipherKey"], match.group(2)),
        table=b64_table,
    )

    operations = algorithm["operations"]

    dashes = conditional_encrypt(
        "-".join(
            str(
                isolated_eval(
                    str(ord(character)) + operations[str(count % len(operations))]
                )
            )
            for count, character in enumerate(
                conditional_encrypt(content_id, algorithm["pre"], b64_table)
            )
        ),
        algorithm["post"],
        b64_table,
    )

    vidstream_info = session.get(f"{match.group(1)}/{algorithm['mainKey']}/{dashes}")

    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json()["data"].get("media", {}).get("sources", [])
    ]
