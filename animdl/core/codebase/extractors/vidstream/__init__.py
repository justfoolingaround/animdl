import functools

import regex

from ...providers.nineanime.decipher import vrf_futoken

EMBED_URL_REGEX = regex.compile(r"(.+?)/(?:e(?:mbed)?)/([a-zA-Z0-9]+)\?t=(.+?)(?:&|$)")


@functools.lru_cache()
def futoken_resolve(session, url):
    return session.get(url).text


def extract(session, url, **opts):
    match = EMBED_URL_REGEX.search(url)
    host = match.group(1)

    futoken = futoken_resolve(session, host + "/futoken")
    data = vrf_futoken(
        session,
        futoken,
        "rawvizcloud" if host != "https://mcloud.to" else "rawmcloud",
        match.group(2),
    )
    vidstream_info = session.get(
        data + f"?t={match.group(3)}",
        headers={"referer": url},
    )

    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json()["result"].get("sources", [])
    ]
