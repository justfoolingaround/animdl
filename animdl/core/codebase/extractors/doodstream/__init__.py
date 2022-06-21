import time

import regex

DOODSTREAM = "https://dood.la/"

PASS_MD5_RE = regex.compile(r"/(pass_md5/.+?)'")
TOKEN_RE = regex.compile(r"\?token=([^&]+)")


def extract(session, url):
    response = session.get(url)

    if not response.status_code < 400:
        return []

    embed_page = session.get(url).text
    has_md5 = PASS_MD5_RE.search(embed_page)

    if not has_md5:
        return []

    has_token = TOKEN_RE.search(embed_page)
    if not has_token:
        return []

    return [
        {
            "stream_url": "{}doodstream?token={}&expiry={}".format(
                session.get(
                    DOODSTREAM + has_md5.group(1), headers={"referer": DOODSTREAM}
                ).text,
                has_token.group(1),
                int(time.time() * 1000),
            ),
            "headers": {"referer": DOODSTREAM},
        }
    ]
